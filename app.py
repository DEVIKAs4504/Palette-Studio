import streamlit as st
from PIL import Image, ImageColor
from collections import Counter
import numpy as np
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, lab2rgb
import colorsys
from PIL import Image, ImageDraw, ImageFont
import io


st.set_page_config(
    page_title="Palette Studio",
    page_icon=":art:",
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown("""
    <style>
         @import url('https://fonts.googleapis.com/css2?family=Gabriela:wght@400;500;600;700&family=Nunito+Sans:wght@400;500;600;700;800&family=Anton+SC&display=swap');
        
        /* Main font across the app */
        html, body, [class*="css"], .stApp {
            font-family: 'Gabriela', sans-serif;
        }

        /* Inputs, dropdowns, sliders, and buttons */
        button, input, textarea, select,
        [data-baseweb="select"],
        [data-baseweb="input"],
        [data-baseweb="slider"],
        [data-testid="stFileUploader"],
        [data-testid="stDownloadButton"] button,
        .stButton button {
            font-family: 'Gabriela', sans-serif !important;
        }

        /* Palette hex codes and code boxes */
        code, pre, .stCode {
            font-family: 'Gabriela', sans-serif !important;
        }
     
        /* Main Palette Studio title only */
        [data-testid="stAppViewContainer"] h1 {
                    font-family: 'Anton SC', sans-serif !important;
                    color: #a4133c !important;
                    font-weight: 400 !important;
                }

         [data-testid="stAppViewContainer"] h3 {
                    font-family: 'Anton SC', sans-serif !important;
                    color: #a4133c !important;
                    font-weight: 400 !important;
                }

        [data-testid="stAppViewContainer"] h4 {
                    font-family: 'Anton SC' !important;
                    color: #a4133c !important;
                    font-size: 20px !important;
                    font-weight: 500 !important;
                }

        [data-testid="stAppViewContainer"] p {
                    font-family: 'Gabriela' !important;
                    color: #69140e !important;
                    font-size: 18px !important;
                    font-weight: 500 !important;
                }
                
        
        /* Image uploader card */
        [data-testid="stFileUploader"] {
                    background-color: #ff928b;
                    border: 6px solid #f08080;
                    border-radius: 16px;
                    padding: 20px;
                    margin-top: 20px;
                }       
                
        [data-testid="stFileUploader"] section {
                    background: #FFFCF7 !important;
                    border: 1.5px dashed #C9AD9A !important;
                    border-radius: 16px !important;
                    padding: 20px !important;
                    transition: background-color 0.25s ease,
                                border-color 0.25s ease,
                                box-shadow 0.25s ease !important;
                }

        [data-testid="stFileUploader"] section:hover {
                    background: #F7F1E8 !important;
                    border-color: #A87960 !important;
                    box-shadow: 0 5px 16px rgba(73, 56, 47, 0.08);
                }

        /* Smooth button inside the uploader */
        [data-testid="stFileUploader"] button {
                    transition: background-color 0.2s ease,
                                transform 0.2s ease !important;
                }

        [data-testid="stFileUploader"] button:hover {
                    transform: translateY(-1px);
                }

        /* Respect reduced-motion preferences */
        @media (prefers-reduced-motion: reduce) {
                [data-testid="stFileUploader"] section,
                [data-testid="stFileUploader"] button {
                    transition: none !important;
                }
        }


        .stButton button,
        [data-testid="stDownloadButton"] button {
            transition: transform 0.22s ease,
                        box-shadow 0.22s ease,
                        background-color 0.22s ease,
                        border-color 0.22s ease !important;
        }

        .stButton button:hover,
        [data-testid="stDownloadButton"] button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 14px rgba(73, 56, 47, 0.12);
            border-color: #A87960 !important;
        }

        .stButton button:active,
        [data-testid="stDownloadButton"] button:active {
            transform: translateY(0);
            box-shadow: none;
        }


        [data-baseweb="select"] > div,
        [data-testid="stFileUploader"] section {
            transition: border-color 0.22s ease,
                        box-shadow 0.22s ease !important;
        }

        [data-baseweb="select"] > div:hover,
        [data-testid="stFileUploader"] section:hover {
            border-color: #A87960 !important;
        }


        @media (prefers-reduced-motion: reduce) {
            .stButton button,
            [data-testid="stDownloadButton"] button,
            [data-baseweb="select"] > div,
            [data-testid="stFileUploader"] section {
                transition: none !important;
            }
        }

        /* Palette swatch hover animation */
        .palette-swatch {
            transition: transform 0.25s ease,
                        box-shadow 0.25s ease,
                        border-color 0.25s ease;
            cursor: pointer;
        }

        .palette-swatch:hover {
            transform: translateY(-4px) scale(1.03);
            box-shadow: 0 7px 16px rgba(73, 56, 47, 0.16);
            border-color: #A87960 !important;
        }

        @media (prefers-reduced-motion: reduce) {
            .palette-swatch {
                transition: none !important;
            }
        }
        /* ─── Palette Studio: Ambient Gradient Fix ─── */

        .stApp {
            background-color: #FFECD1 !important;
            background-image:
                radial-gradient(
                    ellipse at 10% 20%,
                    rgba(200, 79, 155, 0.38),
                    transparent 42%
                ),
                radial-gradient(
                    ellipse at 85% 30%,
                    rgba(224, 60, 169, 0.42),
                    transparent 40%
                ),
                radial-gradient(
                    ellipse at 50% 90%,
                    rgba(177, 100, 198, 0.28),
                    transparent 45%
                ) !important;
            background-size: 160% 160%;
            animation: ambientDrift 10s ease-in-out infinite alternate;
        }

        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        [data-testid="stMainBlockContainer"] {
            background: transparent !important;
        }

        @keyframes ambientDrift {
            0% {
                background-position: 0% 0%, 100% 20%, 50% 100%;
                background-size: 160% 160%;
            }
            50% {
                background-position: 35% 40%, 65% 60%, 20% 70%;
                background-size: 190% 190%;
            }
            100% {
                background-position: 100% 70%, 0% 100%, 80% 20%;
                background-size: 170% 170%;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .stApp {
                animation: none !important;
            }
        }

    </style>
       
""", unsafe_allow_html=True)


st.title("Palette Studio :material/palette:")
st.write("_An image based color palette extractor for artists and designers_")


uploaded_file= st.file_uploader(
    "Upload your image :material/upload:",
    type=["png", "jpeg", "jpg"]
)

psize=st.slider("Choose your palette size :material/brush: ",
                min_value= 3,
                max_value= 12,
                value=8,
                step=1
                )

palettemodes={
    "Overall image mood": "Median Cut",
    "Main colors & color families": "K-means Clustering",
    "Most frequently occuring shades": "Popularity / Frequency"
}

mode=st.selectbox(
    "What kind of palette would you like? ",
    list(palettemodes.keys())
)

algo=palettemodes[mode]


def extract_palette(image, palette_size, algorithm):
    image = image.convert("RGB")
    image.thumbnail((300, 300))

    pixels = np.array(image).reshape(-1, 3)
    unique_pixels = np.unique(pixels, axis=0)

    effective_size = min(palette_size, len(unique_pixels))

    if algorithm == "Median Cut":
        quantized = image.quantize(
            colors=effective_size,
            method=Image.Quantize.MEDIANCUT
        )

        color_counts = quantized.getcolors()
        palette = quantized.getpalette()
        color_counts.sort(reverse=True)

        result = []
        for _, index in color_counts:
            rgb = tuple(palette[index * 3:index * 3 + 3])
            if rgb not in result:
                result.append(rgb)

        return result[:palette_size]

    
    elif algorithm == "K-means Clustering":
  
        pixels_normalized = pixels.reshape(-1, 1, 3) / 255.0
        lab_pixels = rgb2lab(pixels_normalized).reshape(-1, 3)

        effective_size = min(palette_size, len(np.unique(lab_pixels, axis=0)))

        model = KMeans(
            n_clusters=effective_size,
            random_state=42,
            n_init=10
        )

        labels = model.fit_predict(lab_pixels)
        centers_lab = model.cluster_centers_

        counts = Counter(labels)
        order = sorted(
            range(len(centers_lab)),
            key=lambda i: counts[i],
            reverse=True
        )

        result = []
        for i in order:
            center_lab = centers_lab[i].reshape(1, 1, 3)
            center_rgb = lab2rgb(center_lab)[0, 0]
            rgb = tuple(
                np.rint(center_rgb * 255).clip(0, 255).astype(int)
            )
            result.append(rgb)

        return result
    
    elif algorithm == "Popularity / Frequency":
   
        bucket_size = 16

        buckets = (pixels // bucket_size) * bucket_size
        counts = Counter(map(tuple, buckets))

        common_buckets = counts.most_common(palette_size)

        result = []

        for bucket, _ in common_buckets:

            bucket_array = np.array(bucket)

            mask = np.all(
                (pixels // bucket_size) * bucket_size == bucket_array,
                axis=1
            )

            average_rgb = np.mean(pixels[mask], axis=0)
            rgb = tuple(
                np.rint(average_rgb).clip(0, 255).astype(int)
            )

            result.append(rgb)

        return result

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def generate_harmony(hex_color, harmony_type):
    hex_color = hex_color.lstrip("#")

    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    if harmony_type == "Complementary":
        shifts = [0, 0.5]

    elif harmony_type == "Analogous":
        shifts = [0, -1/12, 1/12]

    elif harmony_type == "Triadic":
        shifts = [0, 1/3, 2/3]

    else:
        return [hex_color]

    result = []

    for shift in shifts:
        new_hue = (h + shift) % 1
        nr, ng, nb = colorsys.hsv_to_rgb(new_hue, s, v)

        new_hex = "#{:02X}{:02X}{:02X}".format(
            round(nr * 255),
            round(ng * 255),
            round(nb * 255)
        )

        result.append(new_hex)

    return result


def analyze_palette(palette_colors):
    """Calculate the visual characteristics of a colour palette."""

    analysis = []

    for hex_color in palette_colors:
        hex_color = hex_color.lstrip("#")

        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255

        hue, saturation, value = colorsys.rgb_to_hsv(r, g, b)

        # Approximate perceived brightness on a 0–100 scale
        lightness = (
            0.2126 * r + 0.7152 * g + 0.0722 * b
        ) * 100

        if saturation < 0.20:
            colour_type = "Muted"
        elif saturation < 0.55:
            colour_type = "Moderately saturated"
        else:
            colour_type = "Vivid"

        if lightness >= 70:
            brightness = "Light"
        elif lightness >= 35:
            brightness = "Mid-tone"
        else:
            brightness = "Dark"

        if saturation < 0.10:
            temperature = "Nearly neutral"
        elif 0.08 < hue < 0.17:
            temperature = "Warm-leaning"
        elif 0.45 < hue < 0.72:
            temperature = "Cool-leaning"
        else:
            temperature = "Mixed or hue-dependent"

        analysis.append({
            "hex": "#" + hex_color.upper(),
            "lightness": round(lightness, 1),
            "saturation": round(saturation * 100, 1),
            "brightness": brightness,
            "colour_type": colour_type,
            "temperature": temperature
        })

    return analysis


def createimage(palette_hexes):


    swatch_width = 240
    swatch_height = 180
    label_height = 55
    header_height = 175
    padding = 30

    width = len(palette_hexes) * swatch_width + 2 * padding
    height = swatch_height + label_height +header_height+ 2 * padding

    image = Image.new("RGB", (width, height), "#F7EAE8")
    draw = ImageDraw.Draw(image)
    draw.text(
        (padding, padding),
        "Palette Studio",
        font=ImageFont.load_default(size=60),
        fill="#6F2A27"
    )
    for i, color in enumerate(palette_hexes):
        x = padding + i * swatch_width
        y = padding+ header_height

        draw.rectangle(
            [x, y, x + swatch_width - 1, y + swatch_height],
            fill=color
        )

        draw.text(
            (x + 8, y + swatch_height + 15),
            color.upper(),
            fill="#6F2A27"
        )

    return image


def colordist(image, palette_colors):

    image = image.convert("RGB")
    image.thumbnail((300, 300))

    pixels = np.array(image).reshape(-1, 3).astype(float)
    palette = np.array([
        tuple(int(color.lstrip("#")[i:i + 2], 16)
              for i in (0, 2, 4))
        for color in palette_colors
    ], dtype=float)

    distances = np.sum(
        (pixels[:, None, :] - palette[None, :, :]) ** 2,
        axis=2
    )
    assignments = np.argmin(distances, axis=1)

    counts = np.bincount(
        assignments, minlength=len(palette_colors)
    )

    percentages = counts / len(pixels) * 100

    return percentages.tolist()



if uploaded_file is not None:

    st.image(uploaded_file, caption="_Your uploaded image_")

    img= Image.open(uploaded_file).convert("RGB")
    # st.write("Selected algorithm: ", algo)
    palettecolors= extract_palette( img, psize, algo)
    #st.write("Extracted RGB colors:", palettecolors)
    
    hexpalette=[]

    for rgb in palettecolors:
        hexcode = "#{:02X}{:02X}{:02X}".format(*rgb)
        hexpalette.append(hexcode)
  
    palette_analysis = analyze_palette(hexpalette)
    color_percentages = colordist(img, hexpalette)
    
    st.subheader("Your Color Palette")

    columns=st.columns(psize)

    for i, hexcode in enumerate(hexpalette):
        rgb = tuple(
            int(hexcode[j:j + 2], 16)
            for j in (1, 3, 5)
        )

        with columns[i]:
            st.markdown(
                f"""<div class="palette-swatch"
                style="background-color: {hexcode};
                height: 100px; border-radius: 12px;
                border: 1px solid #E4D8CA;"></div>
                <p style="text-align: center; font-size: 12px;
                font-weight: 600;">{hexcode}</p>""",
                unsafe_allow_html=True
            )
            st.code(hexcode, language=None)

    csspalette= ":root{\n" + "\n".join(
        f" --color-{i+1}:{color};" 
        for i, color in enumerate(hexpalette)
    )+ "\n}"

    
    st.subheader("Palette Preview")

    st.markdown(
        "<div style='display: flex; height: 90px; "
        "border-radius: 14px; overflow: hidden;'>"
        + "".join(
            f"<div style='background-color: {color}; "
            "flex: 1;'></div>"
            for color in hexpalette
        )
        + "</div>",
        unsafe_allow_html=True
    )

    st.write("\n")
    
    st.download_button(
        label="Download palette as CSS",
        data=csspalette,
        file_name="palette.css",
        mime="text/css",
        icon=":material/download:"
    )

    palette_image = createimage(hexpalette)
    
    image_buffer = io.BytesIO()
    palette_image.save(image_buffer, format="PNG")
    
    st.download_button(
        label="Download palette as PNG",
        data=image_buffer.getvalue(),
        file_name="my_palette.png",
        mime="image/png",
        icon=":material/download:"
        )

    st.subheader("Palette Analysis")

    average_lightness = sum(
        item["lightness"] for item in palette_analysis
    ) / len(palette_analysis)

    average_saturation = sum(
        item["saturation"] for item in palette_analysis
    ) / len(palette_analysis)

    if average_lightness >= 65:
        lightness_insight = "This palette has a generally light appearance."
    elif average_lightness >= 35:
        lightness_insight = "This palette has a balanced mix of mid-tone brightness."
    else:
        lightness_insight = "This palette has a generally dark appearance."

    if average_saturation >= 55:
        saturation_insight = "Its colours are highly vivid and saturated."
    elif average_saturation >= 25:
        saturation_insight = "Its colours have moderate saturation."
    else:
        saturation_insight = "Its colours are mostly muted or subdued."

    st.write(lightness_insight)
    st.write(saturation_insight)

    metric1, metric2 = st.columns(2)

    with metric1:
        st.metric("Average Brightness", f"{average_lightness:.1f}%")

    with metric2:
        st.metric("Average Saturation", f"{average_saturation:.1f}%")

    
    st.markdown("#### Colour Distribution")

    st.caption(
        "_Estimated share of the image represented by each palette colour._"
    )

    for hex_code, percentage in zip(hexpalette, color_percentages):
        st.write("")
        st.write("")
        st.markdown(f"**{hex_code}** — {percentage:.1f}%")
        st.markdown(
                f"""
                <div style="background: #E4D8CA; border-radius: 20px;
                            height: 20px; overflow: hidden;">
                    <div style="background: {hex_code};
                                width: {percentage}%; height: 100%;
                                border-radius: 10px;">
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")
    st.markdown("#### Individual Colour Analysis")

    for item in palette_analysis:
        with st.container(border=True):
            st.markdown(
                f"**{item['hex']}** — {item['brightness']} · "
                f"{item['colour_type']}"
            )

            st.caption(
                f"Brightness: {item['lightness']}% | "
                f"Saturation: {item['saturation']}% | "
                f"Temperature: {item['temperature']}"
            )

    
    st.subheader("Color Harmony Studio")
    st.write("Choose a color from your palette to explore matching colors.")

    selected_color = st.selectbox(
        "Choose your base color",
        hexpalette
    )

    harmony_type = st.selectbox(
        "Choose a harmony",
        ["Complementary", "Analogous", "Triadic"]
    )

    harmony_colors = generate_harmony(selected_color, harmony_type)

    harmony_columns = st.columns(len(harmony_colors))

    for i, color in enumerate(harmony_colors):
        with harmony_columns[i]:
            st.markdown(
                f"""
                <div style="
                    background-color: {color};
                    height: 100px;
                    border-radius: 12px;
                    border: 1px solid #E4D8CA;
                "></div>
                <p style="text-align: center; font-weight: 600;">
                    {color}
                </p>
                """,
                unsafe_allow_html=True
            )
  
            st.code(color, language=None)


st.caption("Made for artists, by an artist :material/favorite:", text_alignment="center")
st.caption("Show some love: [@miyokomochii on Instagram](https://www.instagram.com/miyokomochii/)", text_alignment="center")

