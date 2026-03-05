import streamlit as st

def show_receipt(v):
    try:
        # Pura HTML code string mein
        receipt_html = f"""
        <div style="width: 300px; border: 2px solid black; padding: 15px; font-family: monospace; background-color: white; color: black;">
            <h2 style="text-align: center; margin: 0;">( THE LIFE CARE )</h2>
            <p style="text-align: center; font-size: 12px; margin: 5px 0;">MAJEED COLONY SEC 2, KARACHI</p>
            <hr>
            <table style="width: 100%; font-size: 13px;">
                <tr><td><b>Patient:</b></td><td align="right">{v[3]}</td></tr>
                <tr><td><b>Inv #:</b></td><td align="right">{v[1]}</td></tr>
                <tr><td><b>Date:</b></td><td align="right">{v[2]}</td></tr>
                <tr><td><b>Age/Gen:</b></td><td align="right">{v[5]} / {v[6]}</td></tr>
            </table>
            <hr>
            <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid black;">
                    <th align="left">Test Name</th>
                    <th align="right">Amt</th>
                </tr>
        """
        
        # Tests list add karna
        tests = str(v[8]).split(", ")
        for t in tests:
            receipt_html += f"<tr><td>{t}</td><td align='right'>-</td></tr>"
            
        receipt_html += f"""
            </table>
            <hr>
            <div style="display: flex; justify-content: space-between; font-weight: bold;">
                <span>Total:</span> <span>Rs. {v[9]}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Paid:</span> <span>Rs. {v[10]}</span>
            </div>
            <div style="display: flex; justify-content: space-between; background: #eee;">
                <span>Balance:</span> <span>Rs. {v[11]}</span>
            </div>
            <p style="text-align: center; font-size: 10px; margin-top: 20px;">Developed by Zain</p>
        </div>
        """
        
        # Ye line sab se zaroori hai
        st.markdown(receipt_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Galti: {e}")
