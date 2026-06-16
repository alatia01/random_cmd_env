#include <ctype.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "reg_data.h"

#define MAX_NAME_LEN 128

typedef struct {
    char name[MAX_NAME_LEN];
    unsigned width;
    unsigned lsb;
} FieldDef;

typedef struct {
    char name[MAX_NAME_LEN];
    int is_u32_alias;
    FieldDef *fields;
    size_t field_count;
} TypeDef;

typedef struct {
    char type_name[MAX_NAME_LEN];
    char member_name[MAX_NAME_LEN];
    size_t array_len;
    size_t word_offset;
} MemberDef;

typedef struct {
    TypeDef *types;
    size_t type_count;
    MemberDef *members;
    size_t member_count;
} HeaderSpec;

typedef struct {
    const MemberDef *member;
    const TypeDef *type;
    size_t array_index;
    int broadcast_all; /* 1 if [all] was used: write fields to every array slot */
} ActiveSection;

static void *xrealloc(void *ptr, size_t nbytes) {
    void *p = realloc(ptr, nbytes);
    if (!p) {
        fprintf(stderr, "OOM: %zu bytes\n", nbytes);
        exit(1);
    }
    return p;
}

static char *read_text_file(const char *path) {
    FILE *fp = fopen(path, "rb");
    long sz;
    char *buf;
    if (!fp) {
        return NULL;
    }
    if (fseek(fp, 0, SEEK_END) != 0) {
        fclose(fp);
        return NULL;
    }
    sz = ftell(fp);
    if (sz < 0) {
        fclose(fp);
        return NULL;
    }
    if (fseek(fp, 0, SEEK_SET) != 0) {
        fclose(fp);
        return NULL;
    }
    buf = (char *)malloc((size_t)sz + 1);
    if (!buf) {
        fclose(fp);
        return NULL;
    }
    if (fread(buf, 1, (size_t)sz, fp) != (size_t)sz) {
        fclose(fp);
        free(buf);
        return NULL;
    }
    fclose(fp);
    buf[sz] = '\0';
    return buf;
}

static char *trim_left(char *s) {
    while (*s && isspace((unsigned char)*s)) {
        s++;
    }
    return s;
}

static void trim_right(char *s) {
    size_t n = strlen(s);
    while (n > 0 && isspace((unsigned char)s[n - 1])) {
        s[n - 1] = '\0';
        n--;
    }
}

static int starts_with(const char *s, const char *prefix) {
    size_t n = strlen(prefix);
    return strncmp(s, prefix, n) == 0;
}

static const TypeDef *find_type(const HeaderSpec *spec, const char *name) {
    size_t i;
    for (i = 0; i < spec->type_count; i++) {
        if (strcmp(spec->types[i].name, name) == 0) {
            return &spec->types[i];
        }
    }
    return NULL;
}

static const MemberDef *find_member(const HeaderSpec *spec, const char *name, size_t *idx_out) {
    size_t i;
    for (i = 0; i < spec->member_count; i++) {
        if (strcmp(spec->members[i].member_name, name) == 0) {
            if (idx_out) {
                *idx_out = i;
            }
            return &spec->members[i];
        }
    }
    return NULL;
}

static int parse_u32_alias_line(const char *line, char out_name[MAX_NAME_LEN]) {
    char name[MAX_NAME_LEN];
    if (sscanf(line, "typedef uint32_t %127[^;];", name) == 1) {
        strncpy(out_name, name, MAX_NAME_LEN - 1);
        out_name[MAX_NAME_LEN - 1] = '\0';
        return 1;
    }
    return 0;
}

static int parse_reg32_bitfield_line(const char *line, char out_name[MAX_NAME_LEN], unsigned *out_width) {
    const char *p = line;
    char field_name[MAX_NAME_LEN];
    char *dst = field_name;
    unsigned width;

    p = trim_left((char *)p);
    if (!starts_with(p, "REG32")) {
        return 0;
    }
    p += 5;
    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    if (!(*p == '_' || isalpha((unsigned char)*p))) {
        return 0;
    }
    while (*p && (isalnum((unsigned char)*p) || *p == '_')) {
        if ((size_t)(dst - field_name) + 1 < sizeof(field_name)) {
            *dst++ = *p;
        }
        p++;
    }
    *dst = '\0';

    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    if (*p != ':') {
        return 0;
    }
    p++;
    while (*p && isspace((unsigned char)*p)) {
        p++;
    }
    if (sscanf(p, "%u", &width) != 1) {
        return 0;
    }

    strncpy(out_name, field_name, MAX_NAME_LEN - 1);
    out_name[MAX_NAME_LEN - 1] = '\0';
    *out_width = width;
    return 1;
}

static int append_type(HeaderSpec *spec, const TypeDef *type) {
    spec->types = (TypeDef *)xrealloc(spec->types, (spec->type_count + 1) * sizeof(TypeDef));
    spec->types[spec->type_count++] = *type;
    return 0;
}

static int parse_struct_blocks(const char *text, HeaderSpec *spec) {
    const char *p = text;
    while ((p = strstr(p, "typedef struct")) != NULL) {
        const char *lbrace = strchr(p, '{');
        const char *rbrace;
        const char *semi;
        TypeDef t;
        size_t body_len;
        char *body_copy;
        char *line;
        char *saveptr = NULL;
        unsigned lsb = 0;

        if (!lbrace) {
            break;
        }
        rbrace = strchr(lbrace, '}');
        if (!rbrace) {
            break;
        }
        semi = strchr(rbrace, ';');
        if (!semi) {
            break;
        }

        memset(&t, 0, sizeof(t));

        {
            char alias[MAX_NAME_LEN];
            size_t n = 0;
            const char *q = rbrace + 1;
            while (*q && isspace((unsigned char)*q)) {
                q++;
            }
            while (*q && (isalnum((unsigned char)*q) || *q == '_')) {
                if (n + 1 < sizeof(alias)) {
                    alias[n++] = *q;
                }
                q++;
            }
            alias[n] = '\0';
            if (alias[0] == '\0') {
                p = semi + 1;
                continue;
            }
            strncpy(t.name, alias, sizeof(t.name) - 1);
        }

        body_len = (size_t)(rbrace - (lbrace + 1));
        body_copy = (char *)malloc(body_len + 1);
        if (!body_copy) {
            return -1;
        }
        memcpy(body_copy, lbrace + 1, body_len);
        body_copy[body_len] = '\0';

        line = strtok_r(body_copy, "\n", &saveptr);
        while (line) {
            char field_name[MAX_NAME_LEN];
            unsigned width;
            char *clean = trim_left(line);
            trim_right(clean);
            if (parse_reg32_bitfield_line(clean, field_name, &width)) {
                t.fields = (FieldDef *)xrealloc(t.fields, (t.field_count + 1) * sizeof(FieldDef));
                memset(&t.fields[t.field_count], 0, sizeof(FieldDef));
                strncpy(t.fields[t.field_count].name, field_name, MAX_NAME_LEN - 1);
                t.fields[t.field_count].width = width;
                t.fields[t.field_count].lsb = lsb;
                lsb += width;
                t.field_count++;
            }
            line = strtok_r(NULL, "\n", &saveptr);
        }

        free(body_copy);
        if (t.field_count > 0) {
            append_type(spec, &t);
        } else {
            free(t.fields);
        }

        p = semi + 1;
    }
    return 0;
}

static int parse_u32_aliases(const char *text, HeaderSpec *spec) {
    char *copy = strdup(text);
    char *line;
    char *saveptr = NULL;
    if (!copy) {
        return -1;
    }

    line = strtok_r(copy, "\n", &saveptr);
    while (line) {
        char alias[MAX_NAME_LEN];
        char *clean = trim_left(line);
        trim_right(clean);
        if (parse_u32_alias_line(clean, alias)) {
            TypeDef t;
            memset(&t, 0, sizeof(t));
            strncpy(t.name, alias, sizeof(t.name) - 1);
            t.is_u32_alias = 1;
            append_type(spec, &t);
        }
        line = strtok_r(NULL, "\n", &saveptr);
    }

    free(copy);
    return 0;
}

static int parse_member_line(const char *line, char out_type[MAX_NAME_LEN], char out_member[MAX_NAME_LEN], size_t *out_len) {
    char type_name[MAX_NAME_LEN];
    char member_name[MAX_NAME_LEN];
    int n;

    n = sscanf(line, "%127s %127[^;];", type_name, member_name);
    if (n != 2) {
        return 0;
    }

    {
        char *bracket = strchr(member_name, '[');
        if (bracket) {
            char *endb = strchr(bracket + 1, ']');
            if (!endb) {
                return 0;
            }
            *bracket = '\0';
            *out_len = (size_t)strtoul(bracket + 1, NULL, 10);
        } else {
            *out_len = 1;
        }
    }

    strncpy(out_type, type_name, MAX_NAME_LEN - 1);
    out_type[MAX_NAME_LEN - 1] = '\0';
    strncpy(out_member, member_name, MAX_NAME_LEN - 1);
    out_member[MAX_NAME_LEN - 1] = '\0';
    return 1;
}

static int parse_t_reg_vcpi_members(const char *text, HeaderSpec *spec) {
    const char *p = text;
    size_t next_word = 0;

    while ((p = strstr(p, "typedef struct")) != NULL) {
        const char *lbrace = strchr(p, '{');
        const char *rbrace;
        const char *q;
        char alias[MAX_NAME_LEN];
        size_t n = 0;

        if (!lbrace) {
            break;
        }
        rbrace = strchr(lbrace, '}');
        if (!rbrace) {
            break;
        }

        q = rbrace + 1;
        while (*q && isspace((unsigned char)*q)) {
            q++;
        }
        while (*q && (isalnum((unsigned char)*q) || *q == '_')) {
            if (n + 1 < sizeof(alias)) {
                alias[n++] = *q;
            }
            q++;
        }
        alias[n] = '\0';

        if (strcmp(alias, "t_reg_vcpi") == 0) {
            char *body;
            char *line;
            char *saveptr = NULL;

            body = (char *)malloc((size_t)(rbrace - lbrace));
            if (!body) {
                return -1;
            }
            memcpy(body, lbrace + 1, (size_t)(rbrace - lbrace - 1));
            body[rbrace - lbrace - 1] = '\0';

            line = strtok_r(body, "\n", &saveptr);
            while (line) {
                char type_name[MAX_NAME_LEN];
                char member_name[MAX_NAME_LEN];
                size_t arr_len;
                char *clean = trim_left(line);
                trim_right(clean);

                if (parse_member_line(clean, type_name, member_name, &arr_len)) {
                    const TypeDef *type = find_type(spec, type_name);
                    if (type) {
                        MemberDef m;
                        memset(&m, 0, sizeof(m));
                        strncpy(m.type_name, type_name, sizeof(m.type_name) - 1);
                        strncpy(m.member_name, member_name, sizeof(m.member_name) - 1);
                        m.array_len = arr_len;
                        m.word_offset = next_word;

                        spec->members = (MemberDef *)xrealloc(spec->members, (spec->member_count + 1) * sizeof(MemberDef));
                        spec->members[spec->member_count++] = m;
                        next_word += arr_len;
                    }
                }

                line = strtok_r(NULL, "\n", &saveptr);
            }

            free(body);
            return 0;
        }

        p = rbrace + 1;
    }

    return -1;
}

static int load_header_spec(const char *header_path, HeaderSpec *spec) {
    char *text = read_text_file(header_path);
    memset(spec, 0, sizeof(*spec));
    if (!text) {
        return -1;
    }
    if (parse_u32_aliases(text, spec) != 0) {
        free(text);
        return -1;
    }
    if (parse_struct_blocks(text, spec) != 0) {
        free(text);
        return -1;
    }
    if (parse_t_reg_vcpi_members(text, spec) != 0) {
        free(text);
        return -1;
    }
    free(text);
    return 0;
}

static void free_header_spec(HeaderSpec *spec) {
    size_t i;
    for (i = 0; i < spec->type_count; i++) {
        free(spec->types[i].fields);
    }
    free(spec->types);
    free(spec->members);
    memset(spec, 0, sizeof(*spec));
}

static int extract_section_name(const char *line, char out_name[MAX_NAME_LEN]) {
    const char *p = line;
    size_t best_len = 0;
    const char *best = NULL;

    while (*p) {
        if (isupper((unsigned char)*p)) {
            const char *start = p;
            size_t len = 0;
            while (isupper((unsigned char)*p) || isdigit((unsigned char)*p) || *p == '_') {
                p++;
                len++;
            }
            if (len > best_len) {
                best = start;
                best_len = len;
            }
        } else {
            p++;
        }
    }

    if (!best || best_len == 0 || best_len >= MAX_NAME_LEN) {
        return 0;
    }
    memcpy(out_name, best, best_len);
    out_name[best_len] = '\0';
    return 1;
}

static int parse_kv_line(const char *line, char out_key[MAX_NAME_LEN], uint32_t *out_val) {
    /* Accept both ':' and '=' as key-value separator (FR-008 contract v2). */
    const char *sep = NULL;
    const char *colon = strchr(line, ':');
    const char *equals = strchr(line, '=');
    char key[MAX_NAME_LEN];
    char value_text[128];
    char *endptr;
    unsigned long long v;

    /* Pick the first separator that appears. */
    if (colon && equals) {
        sep = (colon < equals) ? colon : equals;
    } else if (colon) {
        sep = colon;
    } else if (equals) {
        sep = equals;
    }
    if (!sep) {
        return 0;
    }

    {
        size_t key_len = (size_t)(sep - line);
        while (key_len > 0 && isspace((unsigned char)line[key_len - 1])) {
            key_len--;
        }
        if (key_len == 0 || key_len >= sizeof(key)) {
            return 0;
        }
        memcpy(key, line, key_len);
        key[key_len] = '\0';
    }

    {
        const char *vstart = sep + 1;
        while (*vstart && isspace((unsigned char)*vstart)) {
            vstart++;
        }
        if (*vstart == '\0') {
            return 0;
        }
        strncpy(value_text, vstart, sizeof(value_text) - 1);
        value_text[sizeof(value_text) - 1] = '\0';
        trim_right(value_text);
    }

    v = strtoull(value_text, &endptr, 0);
    if (endptr == value_text || *endptr != '\0') {
        return 0;
    }
    if (v > 0xFFFFFFFFULL) {
        return 0;
    }

    strncpy(out_key, key, MAX_NAME_LEN - 1);
    out_key[MAX_NAME_LEN - 1] = '\0';
    *out_val = (uint32_t)v;
    return 1;
}

static int set_bitfield_value(uint32_t *word, const TypeDef *type, const char *field_name, uint32_t value) {
    size_t i;
    for (i = 0; i < type->field_count; i++) {
        const FieldDef *f = &type->fields[i];
        if (strcmp(f->name, field_name) == 0) {
            uint32_t mask;
            if (f->width == 32) {
                mask = 0xFFFFFFFFu;
            } else {
                uint32_t maxv = (1u << f->width) - 1u;
                if (value > maxv) {
                    fprintf(stderr, "Value overflow: %s=%u, width=%u\n", field_name, value, f->width);
                    return -1;
                }
                mask = maxv << f->lsb;
            }
            *word &= ~mask;
            *word |= (value << f->lsb) & mask;
            return 0;
        }
    }
    return -1;
}

static uint32_t extract_bitfield_value(uint32_t word, const FieldDef *field) {
    if (field->width >= 32) {
        return word;
    }
    return (word >> field->lsb) & ((1u << field->width) - 1u);
}

static size_t get_printable_field_name_width(const TypeDef *type) {
    size_t i;
    size_t max_width = 0;
    if (!type) {
        return 0;
    }
    for (i = 0; i < type->field_count; i++) {
        const FieldDef *field = &type->fields[i];
        size_t width;
        if (starts_with(field->name, "rsvd")) {
            continue;
        }
        width = strlen(field->name);
        if (width > max_width) {
            max_width = width;
        }
    }
    return max_width;
}

/* Return the index of field_name inside type->fields[], or -1 if not found.
 * Used for duplicate-field detection (FR-010d). */
static int find_field_idx(const TypeDef *type, const char *field_name) {
    size_t i;
    for (i = 0; i < type->field_count; i++) {
        if (strcmp(type->fields[i].name, field_name) == 0) {
            return (int)i;
        }
    }
    return -1;
}

/* Parse the array suffix after a member name in a section-head comment line.
 *
 * Looks for the FIRST '[' occurring after the end of the uppercase token
 * already extracted by extract_section_name().
 *
 * Returns:
 *   0  - no bracket found (non-array or omitted): *index_out unchanged
 *   1  - found [N] with decimal N: *index_out = N
 *   2  - found [all]:               *index_out = SIZE_MAX (broadcast sentinel)
 *  -1  - malformed bracket (skip section head, not fatal)
 */
static int parse_section_array_suffix(const char *line, const char *member_name,
                                      size_t *index_out) {
    /* Find member_name in line, then look for '[' after it. */
    const char *pos = strstr(line, member_name);
    if (!pos) {
        return 0;
    }
    pos += strlen(member_name);
    /* Skip whitespace between member name and '['. */
    while (*pos && isspace((unsigned char)*pos)) {
        pos++;
    }
    if (*pos != '[') {
        return 0; /* no bracket */
    }
    pos++; /* skip '[' */
    /* Check for "all]" keyword. */
    if (strncmp(pos, "all]", 4) == 0) {
        *index_out = (size_t)-1; /* SIZE_MAX-style broadcast sentinel */
        return 2;
    }
    /* Parse decimal index. */
    {
        char *endptr = NULL;
        unsigned long idx = strtoul(pos, &endptr, 10);
        if (endptr == pos || *endptr != ']') {
            return -1; /* malformed */
        }
        *index_out = (size_t)idx;
        return 1;
    }
}

int parse_cmd_cfg_to_vcpi(const char *cfg_path, const char *header_path, t_reg_vcpi *out_vcpi) {
    HeaderSpec spec;
    FILE *fp;
    char line[512];
    ActiveSection active;
    size_t *section_seen = NULL;
    size_t *array_seen_offset = NULL;
    uint8_t *array_section_seen = NULL;
    size_t array_seen_total = 0;
    /* Per-section field-seen bitmask (up to 64 fields per type).
     * Reset to 0 when entering each new section.  Bits are indexed by
     * the field's position in type->fields[].
     * Used to detect duplicate fields within one section (FR-010d). */
    uint64_t active_field_mask = 0;

    if (!out_vcpi) {
        return -1;
    }
    memset(out_vcpi, 0, sizeof(*out_vcpi));
    memset(&active, 0, sizeof(active));

    if (load_header_spec(header_path, &spec) != 0) {
        fprintf(stderr, "Failed to parse header spec: %s\n", header_path);
        return -1;
    }

    section_seen = (size_t *)calloc(spec.member_count, sizeof(size_t));
    if (!section_seen) {
        free_header_spec(&spec);
        return -1;
    }

    /* Track whether MEMBER[N] has already appeared in cfg.
     * Flatten all member array slots into one bitmap for O(1) checks.
     * This enforces FR-010g: duplicate array sections must fail-fast. */
    array_seen_offset = (size_t *)calloc(spec.member_count + 1, sizeof(size_t));
    if (!array_seen_offset) {
        free(section_seen);
        free_header_spec(&spec);
        return -1;
    }
    {
        size_t mi;
        for (mi = 0; mi < spec.member_count; mi++) {
            size_t len = spec.members[mi].array_len > 0 ? spec.members[mi].array_len : 1;
            array_seen_offset[mi] = array_seen_total;
            array_seen_total += len;
        }
        array_seen_offset[spec.member_count] = array_seen_total;
    }
    array_section_seen = (uint8_t *)calloc(array_seen_total, sizeof(uint8_t));
    if (!array_section_seen) {
        free(array_seen_offset);
        free(section_seen);
        free_header_spec(&spec);
        return -1;
    }

    fp = fopen(cfg_path, "r");
    if (!fp) {
        free(array_section_seen);
        free(array_seen_offset);
        free(section_seen);
        free_header_spec(&spec);
        fprintf(stderr, "Cannot open cfg: %s\n", cfg_path);
        return -1;
    }

    while (fgets(line, sizeof(line), fp)) {
        char *clean = trim_left(line);
        trim_right(clean);

        if (*clean == '\0') {
            continue;
        }

        if (*clean == '#') {
            char section[MAX_NAME_LEN];
            size_t member_idx;
            const MemberDef *m;
            const TypeDef *type;
            int suffix_ret;
            size_t explicit_idx = (size_t)-2; /* sentinel: no bracket seen */

            if (!extract_section_name(clean, section)) {
                continue;
            }
            m = find_member(&spec, section, &member_idx);
            if (!m) {
                active.member = NULL;
                active.type = NULL;
                active_field_mask = 0;
                continue;
            }
            type = find_type(&spec, m->type_name);
            if (!type) {
                active.member = NULL;
                active.type = NULL;
                active_field_mask = 0;
                continue;
            }

            /* Parse explicit [N] or [all] suffix from the section head. */
            suffix_ret = parse_section_array_suffix(clean, section, &explicit_idx);

            active.member = m;
            active.type = type;
            active.broadcast_all = 0;
            active_field_mask = 0; /* reset duplicate tracking for new section */

            if (suffix_ret == 2) {
                /* [all]: broadcast subsequent fields to every array slot. */
                {
                    size_t ai;
                    size_t base = array_seen_offset[member_idx];
                    for (ai = 0; ai < m->array_len; ai++) {
                        if (array_section_seen[base + ai]) {
                            fprintf(stderr,
                                    "Duplicate array section '%s[%zu]'\n",
                                    m->member_name, ai);
                            fclose(fp);
                            free(array_section_seen);
                            free(array_seen_offset);
                            free(section_seen);
                            free_header_spec(&spec);
                            return -1;
                        }
                    }
                    for (ai = 0; ai < m->array_len; ai++) {
                        array_section_seen[base + ai] = 1;
                    }
                }
                active.broadcast_all = 1;
                active.array_index = 0;
                /* Zero out all slots upfront so any field that is NOT set
                 * retains 0 (consistent with the missing-field default). */
                {
                    size_t ai;
                    for (ai = 0; ai < m->array_len; ai++) {
                        ((uint32_t *)out_vcpi)[m->word_offset + ai] = 0;
                    }
                }
            } else if (suffix_ret == 1) {
                /* Explicit [N]: route to that exact slot. */
                if (explicit_idx >= m->array_len) {
                    fprintf(stderr,
                            "Array index %zu out of range for member '%s' (len=%zu)\n",
                            explicit_idx, m->member_name, m->array_len);
                    fclose(fp);
                    free(array_section_seen);
                    free(array_seen_offset);
                    free(section_seen);
                    free_header_spec(&spec);
                    return -1;
                }
                {
                    size_t slot = array_seen_offset[member_idx] + explicit_idx;
                    if (array_section_seen[slot]) {
                        fprintf(stderr,
                                "Duplicate array section '%s[%zu]'\n",
                                m->member_name, explicit_idx);
                        fclose(fp);
                        free(array_section_seen);
                        free(array_seen_offset);
                        free(section_seen);
                        free_header_spec(&spec);
                        return -1;
                    }
                    array_section_seen[slot] = 1;
                }
                active.array_index = explicit_idx;
                ((uint32_t *)out_vcpi)[m->word_offset + active.array_index] = 0;
            } else {
                /* No bracket: fall back to sequential counter (legacy behaviour). */
                active.array_index = section_seen[member_idx];
                if (active.array_index >= m->array_len) {
                    active.array_index = m->array_len - 1;
                }
                {
                    size_t slot = array_seen_offset[member_idx] + active.array_index;
                    if (array_section_seen[slot]) {
                        fprintf(stderr,
                                "Duplicate array section '%s[%zu]'\n",
                                m->member_name, active.array_index);
                        fclose(fp);
                        free(array_section_seen);
                        free(array_seen_offset);
                        free(section_seen);
                        free_header_spec(&spec);
                        return -1;
                    }
                    array_section_seen[slot] = 1;
                }
                if (section_seen[member_idx] + 1 < m->array_len) {
                    section_seen[member_idx]++;
                }
                ((uint32_t *)out_vcpi)[m->word_offset + active.array_index] = 0;
            }
            continue;
        }

        if (active.member && active.type) {
            char key[MAX_NAME_LEN];
            uint32_t value;

            if (!parse_kv_line(clean, key, &value)) {
                continue;
            }

            if (active.type->is_u32_alias) {
                /* Scalar uint32_t alias: write directly to all broadcast
                 * slots or the single active slot. */
                if (active.broadcast_all) {
                    size_t ai;
                    for (ai = 0; ai < active.member->array_len; ai++) {
                        ((uint32_t *)out_vcpi)[active.member->word_offset + ai] = value;
                    }
                } else {
                    ((uint32_t *)out_vcpi)[active.member->word_offset + active.array_index] = value;
                }
            } else {
                /* Struct type: validate field exists (unknown → fail, FR-010b)
                 * and check for duplicates within this section (FR-010d). */
                int fidx = find_field_idx(active.type, key);
                if (fidx < 0) {
                    fprintf(stderr, "Unknown field '%s' in section '%s'\n",
                            key, active.member->member_name);
                    fclose(fp);
                    free(array_section_seen);
                    free(array_seen_offset);
                    free(section_seen);
                    free_header_spec(&spec);
                    return -1;
                }
                /* Duplicate detection (only tracks up to 64 fields). */
                if (fidx < 64) {
                    uint64_t bit = (uint64_t)1 << fidx;
                    if (active_field_mask & bit) {
                        fprintf(stderr,
                                "Duplicate field '%s' in section '%s'\n",
                                key, active.member->member_name);
                        fclose(fp);
                        free(array_section_seen);
                        free(array_seen_offset);
                        free(section_seen);
                        free_header_spec(&spec);
                        return -1;
                    }
                    active_field_mask |= bit;
                }

                if (active.broadcast_all) {
                    size_t ai;
                    for (ai = 0; ai < active.member->array_len; ai++) {
                        uint32_t *tw = &((uint32_t *)out_vcpi)[active.member->word_offset + ai];
                        if (set_bitfield_value(tw, active.type, key, value) != 0) {
                            /* Should not happen since fidx was already validated. */
                            fprintf(stderr, "Internal error writing field '%s'\n", key);
                            fclose(fp);
                            free(array_section_seen);
                            free(array_seen_offset);
                            free(section_seen);
                            free_header_spec(&spec);
                            return -1;
                        }
                    }
                } else {
                    uint32_t *tw = &((uint32_t *)out_vcpi)[active.member->word_offset + active.array_index];
                    if (set_bitfield_value(tw, active.type, key, value) != 0) {
                        /* Should not happen since fidx was already validated. */
                        fprintf(stderr, "Internal error writing field '%s'\n", key);
                        fclose(fp);
                        free(array_section_seen);
                        free(array_seen_offset);
                        free(section_seen);
                        free_header_spec(&spec);
                        return -1;
                    }
                }
            }
        }
    }

    fclose(fp);
    free(array_section_seen);
    free(array_seen_offset);
    free(section_seen);
    free_header_spec(&spec);
    return 0;
}

int print_vcpi_debug_dump(const char *header_path, const t_reg_vcpi *vcpi) {
    HeaderSpec spec;
    size_t i;
    const uint32_t *words;

    if (!vcpi) {
        return -1;
    }
    if (load_header_spec(header_path, &spec) != 0) {
        fprintf(stderr, "Failed to parse header spec for debug dump: %s\n", header_path);
        return -1;
    }

    words = (const uint32_t *)vcpi;
    for (i = 0; i < spec.member_count; i++) {
        const MemberDef *m = &spec.members[i];
        const TypeDef *type = find_type(&spec, m->type_name);
        size_t field_name_width = get_printable_field_name_width(type);
        size_t j;
        if (m->array_len == 1) {
            printf("%s = 0x%08X\n", m->member_name, words[m->word_offset]);
            if (type && !type->is_u32_alias) {
                size_t k;
                for (k = 0; k < type->field_count; k++) {
                    const FieldDef *field = &type->fields[k];
                    if (starts_with(field->name, "rsvd")) {
                        continue;
                    }
                    printf("    %*s = %-10u\n", (int)field_name_width, field->name, extract_bitfield_value(words[m->word_offset], field));
                }
            }
        } else {
            for (j = 0; j < m->array_len; j++) {
                printf("%s[%zu] = 0x%08X\n", m->member_name, j, words[m->word_offset + j]);
                if (type && !type->is_u32_alias) {
                    size_t k;
                    for (k = 0; k < type->field_count; k++) {
                        const FieldDef *field = &type->fields[k];
                        if (starts_with(field->name, "rsvd")) {
                            continue;
                        }
                        printf("    %*s = %-10u\n", (int)field_name_width, field->name, extract_bitfield_value(words[m->word_offset + j], field));
                    }
                }
            }
        }
    }

    free_header_spec(&spec);
    return 0;
}

/* Demo API: replace this with your real API symbol. */
void vcpi_submit_api(const t_reg_vcpi *i) {
    printf("API called, first register=0x%08X\n", ((const uint32_t *)i)[0]);
}

/* By-value wrapper: accepts a t_reg_vcpi by value, internally forwards to
 * vcpi_submit_api via pointer.  Provided for callers that prefer value
 * semantics (FR-010c). */
void vcpi_submit_api_by_value(t_reg_vcpi vcpi) {
    vcpi_submit_api(&vcpi);
}

int main(int argc, char **argv) {
    const char *cfg_path = "cmd.cfg";
    const char *header_path = "reg_data.h";
    int dump_enabled = 0;
    int positional = 0;
    int argi;
    t_reg_vcpi i;

    for (argi = 1; argi < argc; argi++) {
        const char *arg = argv[argi];
        if (strcmp(arg, "--dump") == 0 || strcmp(arg, "-d") == 0) {
            dump_enabled = 1;
            continue;
        }
        if (strcmp(arg, "--no-dump") == 0) {
            dump_enabled = 0;
            continue;
        }
        if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            printf("Usage: %s [cfg_path] [header_path] [--dump|-d] [--no-dump]\n", argv[0]);
            return 0;
        }
        if (arg[0] == '-') {
            fprintf(stderr, "Unknown option: %s\n", arg);
            fprintf(stderr, "Usage: %s [cfg_path] [header_path] [--dump|-d] [--no-dump]\n", argv[0]);
            return 1;
        }

        if (positional == 0) {
            cfg_path = arg;
            positional++;
        } else if (positional == 1) {
            header_path = arg;
            positional++;
        } else {
            fprintf(stderr, "Too many positional arguments: %s\n", arg);
            fprintf(stderr, "Usage: %s [cfg_path] [header_path] [--dump|-d] [--no-dump]\n", argv[0]);
            return 1;
        }
    }

    if (parse_cmd_cfg_to_vcpi(cfg_path, header_path, &i) != 0) {
        fprintf(stderr, "Parse failed\n");
        return 1;
    }

    if (dump_enabled) {
        if (print_vcpi_debug_dump(header_path, &i) != 0) {
            fprintf(stderr, "Debug dump failed\n");
            return 1;
        }
    }

    /* Parsed data is passed to API as t_reg_vcpi i. */
    vcpi_submit_api(&i);
    return 0;
}
