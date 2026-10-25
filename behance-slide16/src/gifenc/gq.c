// Small helpers for the GIF encoder: serpentine Floyd-Steinberg dither limited to a mask,
// and the GIF variant of LZW with its 255-byte sub-blocks.
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static inline float clampf(float v) { return v < 0 ? 0 : (v > 255 ? 255 : v); }
// dm: 1 where error diffusion is wanted (the photo), 0 for crisp graphics (text, UI, flat white)
void fs_dither(const float *img, const uint8_t *mask, const uint8_t *dm, int h, int w, const float *pal, int k, float strength, uint8_t *out) {
    float *e0 = calloc((w + 2) * 3, sizeof(float)), *e1 = calloc((w + 2) * 3, sizeof(float));
    for (int y = 0; y < h; y++) {
        int dir = (y & 1) ? -1 : 1, x0 = dir > 0 ? 0 : w - 1;
        memset(e1, 0, (w + 2) * 3 * sizeof(float));
        for (int i = 0, x = x0; i < w; i++, x += dir) {
            int p = y * w + x;
            if (!mask[p]) continue;
            float c[3];
            for (int ch = 0; ch < 3; ch++) c[ch] = clampf(img[p * 3 + ch] + (dm[p] ? e0[(x + 1) * 3 + ch] : 0));
            int best = 0; float bd = 1e30f;
            for (int j = 0; j < k; j++) {
                float dr = c[0] - pal[j * 3], dg = c[1] - pal[j * 3 + 1], db = c[2] - pal[j * 3 + 2];
                float d = 2 * dr * dr + 4 * dg * dg + 3 * db * db;
                if (d < bd) { bd = d; best = j; }
            }
            out[p] = best;
            if (!dm[p]) continue;
            for (int ch = 0; ch < 3; ch++) {
                float er = (c[ch] - pal[best * 3 + ch]) * strength;
                int xn = x + dir;
                if (xn >= 0 && xn < w && mask[p + dir]) e0[(xn + 1) * 3 + ch] += er * 7 / 16;
                e1[(x - dir + 1) * 3 + ch] += er * 3 / 16;
                e1[(x + 1) * 3 + ch] += er * 5 / 16;
                e1[(x + dir + 1) * 3 + ch] += er * 1 / 16;
            }
        }
        float *t = e0; e0 = e1; e1 = t;
    }
    free(e0); free(e1);
}
// returns number of bytes written to out (sub-blocks plus the 0 terminator)
typedef struct { uint8_t *out; int pos, blk; uint8_t buf[256]; int nb; uint32_t acc; int bits; } W;
static void flushb(W *s) { if (s->nb) { s->out[s->pos++] = s->nb; memcpy(s->out + s->pos, s->buf, s->nb); s->pos += s->nb; s->nb = 0; } }
static void put(W *s, int code, int size) {
    s->acc |= (uint32_t)code << s->bits; s->bits += size;
    while (s->bits >= 8) { s->buf[s->nb++] = s->acc & 255; s->acc >>= 8; s->bits -= 8; if (s->nb == 255) flushb(s); }
}
int lzw(const uint8_t *idx, int n, int minc, uint8_t *out) {
    W s = { out, 0, 0, {0}, 0, 0, 0 };
    int clear = 1 << minc, eoi = clear + 1, next = eoi + 1, size = minc + 1;
    int *tab = malloc(sizeof(int) * 4096 * 256);   // tab[prefix*256+byte] = code, -1 none
    memset(tab, -1, sizeof(int) * 4096 * 256);
    put(&s, clear, size);
    int pre = idx[0];
    for (int i = 1; i < n; i++) {
        int c = idx[i], key = pre * 256 + c;
        if (tab[key] >= 0) { pre = tab[key]; continue; }
        put(&s, pre, size);
        if (next < 4096) { tab[key] = next++; if (next > (1 << size) && size < 12) size++; }
        else { put(&s, clear, size); memset(tab, -1, sizeof(int) * 4096 * 256); next = eoi + 1; size = minc + 1; }
        pre = c;
    }
    put(&s, pre, size); put(&s, eoi, size);
    if (s.bits) { s.buf[s.nb++] = s.acc & 255; if (s.nb == 255) flushb(&s); }
    flushb(&s); out[s.pos++] = 0;
    free(tab); return s.pos;
}
