import streamlit as st

def show_loader(message="Loading..."):
    spinner_html = f"""
    <style>
    .spm-loader-overlay {{
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: #1a3863;
        z-index: 9999999;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    .spm-bounce {{
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 4rem;
        font-weight: bold;
        letter-spacing: 0.1em;
        color: #fff;
        margin-bottom: 24px;
        display: flex;
        align-items: flex-end;
        gap: 0.10em;
    }}
    .spm-bounce span {{
        display: inline-block;
        animation: bounce 1s infinite alternate;
    }}
    .spm-bounce .spm-m {{
        color: #f7c948;
        animation-delay: 0.2s;
    }}
    .spm-bounce .spm-s {{ animation-delay: 0.0s; }}
    .spm-bounce .spm-p {{ animation-delay: 0.1s; }}
    @keyframes bounce {{
        0%   {{ transform: translateY(0); }}
        50%  {{ transform: translateY(-20px); }}
        100% {{ transform: translateY(0); }}
    }}
    .spm-loader-text {{
        font-size:1.3rem;
        color: #fff;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-align: center;
        margin-top: 12px;
    }}
    /* Cover sidebar */
    [data-testid="stSidebar"] {{
        z-index: 0 !important;
    }}
    </style>
    <div class="spm-loader-overlay" id="spm-loader-overlay">
        <div class="spm-bounce">
            <span class="spm-s">S</span>
            <span class="spm-p">P</span>
            <span class="spm-m">M</span>
        </div>
        <div class="spm-loader-text">{message}</div>
    </div>
    """
    # Return the placeholder and HTML to control loader outside this function
    return st.empty(), spinner_html
