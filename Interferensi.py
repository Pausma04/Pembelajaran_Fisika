# Simulasi Interferensi Pembelajaran Fisika
import streamlit as st
import math
import matplotlib.pyplot as plt
from matplotlib import patches

# ==========================================================
# FUNGSI PERHITUNGAN INTERFERENSI
# ==========================================================
def compute_intensity_1d(x, a, d, wavelength, L):
    theta = np.arctan2(x, L)
    beta = (np.pi * a * np.sin(theta)) / wavelength
    beta = np.where(np.abs(beta) < 1e-12, 1e-12, beta)
    envelope = (np.sin(beta) / beta)**2
    gamma = (np.pi * d * np.sin(theta)) / wavelength
    interference = np.cos(gamma)**2
    return envelope * interference

def make_interference_image(a, d, wavelength, L,
                            screen_width=0.04, screen_height=0.02,
                            nx=2000, ny=400, use_noise=True):

    x = np.linspace(-screen_width/2, screen_width/2, nx)
    I1d = compute_intensity_1d(x, a, d, wavelength, L)
    I1d = I1d / I1d.max()

    y = np.linspace(-screen_height/2, screen_height/2, ny)
    sigma_y = screen_height * 0.06
    vertical = np.exp(-0.5 * (y / sigma_y)**2)
    vertical /= vertical.max()

    I2d = np.outer(vertical, I1d)

    if use_noise:
        noise = 0.010 * np.random.randn(*I2d.shape)
        I2d = np.clip(I2d + noise, 0, None)

    return I2d / I2d.max(), x, y


# ==========================================================
# PARAMETER AWAL
# ==========================================================
a0 = 0.1e-3
d0 = 0.5e-3
w0 = 650e-9
L0 = 1.0

I2d, x, y = make_interference_image(a0, d0, w0, L0)


# ==========================================================
# FIGURE & AXES — LAYOUT FIXED
# ==========================================================
fig = plt.figure(figsize=(12, 6))

# Area gambar utama (besar)
ax_img = fig.add_axes([0.08, 0.32, 0.80, 0.62])

im = ax_img.imshow(
    I2d,
    extent=[x[0]*1000, x[-1]*1000, y[0]*1000, y[-1]*1000],
    origin="lower",
    aspect="auto",
    cmap="inferno"
)
ax_img.set_xlabel("Posisi horisontal di layar (mm)")
ax_img.set_ylabel("Posisi vertikal di layar (mm)")

# Title besar
ax_img.set_title(
    f"Interferensi 2D — λ={650} nm, d={d0*1e3:.2f} mm, a={a0*1e3:.2f} mm, L={L0:.2f} m"
)

# Colorbar (rapi & tidak tumpang tindih)
cbar_ax = fig.add_axes([0.90, 0.32, 0.02, 0.62])
cbar = fig.colorbar(im, cax=cbar_ax)
cbar.set_label("Intensitas (norm.)")


# ==========================================================
# CHECKBOX NOISE DI POJOK KANAN ATAS
# ==========================================================
check_ax = fig.add_axes([0.83, 0.20, 0.10, 0.08])
check = CheckButtons(check_ax, ["Noise"], [True])


# ==========================================================
# SLIDER PANEL DI BAWAH — RAPI & TIDAK TUMPANG TINDIH
# ==========================================================
slider_height = 0.04
ax_a  = fig.add_axes([0.12, 0.24, 0.70, slider_height])
ax_d  = fig.add_axes([0.12, 0.19, 0.70, slider_height])
ax_wl = fig.add_axes([0.12, 0.14, 0.70, slider_height])
ax_L  = fig.add_axes([0.12, 0.09, 0.70, slider_height])

s_a  = Slider(ax_a,  "Lebar celah a (mm)",   0.01, 1.00, valinit=a0*1e3)
s_d  = Slider(ax_d,  "Jarak antar celah d (mm)", 0.05, 2.00, valinit=d0*1e3)
s_wl = Slider(ax_wl, "λ (nm)", 380, 780, valinit=w0*1e9)
s_L  = Slider(ax_L,  "Jarak layar L (m)", 0.2, 3.0, valinit=L0)

# Tombol reset
reset_ax = fig.add_axes([0.83, 0.09, 0.12, 0.05])
btn_reset = Button(reset_ax, "Reset")


# ==========================================================
# UPDATE FUNCTION
# ==========================================================
def update(val):
    a = s_a.val * 1e-3
    d = s_d.val * 1e-3
    wl = s_wl.val * 1e-9
    L  = s_L.val

    use_noise = check.get_status()[0]

    I2d_new, x_new, y_new = make_interference_image(a, d, wl, L, use_noise=use_noise)

    im.set_data(I2d_new)
    im.set_extent([x_new[0]*1000, x_new[-1]*1000, y_new[0]*1000, y_new[-1]*1000])
    im.set_clim(0, I2d_new.max())

    ax_img.set_title(
        f"Interferensi 2D — λ={s_wl.val:.0f} nm, d={s_d.val:.2f} mm, a={s_a.val:.2f} mm, L={s_L.val:.2f} m"
    )

    fig.canvas.draw_idle()

s_a.on_changed(update)
s_d.on_changed(update)
s_wl.on_changed(update)
s_L.on_changed(update)
check.on_clicked(lambda x: update(None))

btn_reset.on_clicked(lambda x: [s_a.reset(), s_d.reset(), s_wl.reset(), s_L.reset()])



plt.show()

