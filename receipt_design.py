import streamlit as st
import streamlit.components.v1 as components

def show_receipt(v):
    try:
        # Lab Contact number session state se uthayein (Default agar na mile)
        lab_phone = st.session_state.get('lab_phone', '03XX-XXXXXXX')
        
        # Tests aur unke rates ki setting
        tests_list = str(v[8]).split(", ")
        total_bill = float(v[9])
        
        # Har test ka average rate (Amt fix)
        per_test_rate = total_bill / len(tests_list) if len(tests_list) > 0 else 0
        
        test_rows = ""
        for t in tests_list:
            test_rows += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 8px 0; font-size: 14px;">{t}</td>
                <td align="right" style="padding: 8px 0; font-size: 14px;">Rs. {per_test_rate:.0f}</td>
            </tr>"""

        # HTML Slip Code
        receipt_html = f"""
        <html>
        <head>
            <style>
                @media print {{
                    @page {{ size: auto; margin: 0mm; }}
                    body {{ background: white; }}
                    .no-print {{ display: none !important; }}
                    .receipt-container {{ border: none !important; box-shadow: none !important; padding: 10px !important; }}
                }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                .receipt-container {{
                    width: 420px;
                    margin: 0 auto;
                    padding: 20px;
                    background: white;
                    border: 1px solid #eee;
                }}
                .header {{ text-align: center; border-bottom: 3px solid #000; padding-bottom: 10px; }}
                .btn-print {{ 
                    background: #2e7d32; color: white; border: none; padding: 12px 20px; 
                    border-radius: 5px; cursor: pointer; font-weight: bold; width: 100%; margin-bottom: 20px;
                    font-size: 16px;
                }}
            </style>
        </head>
        <body>
            <button class="btn-print no-print" onclick="window.print()">CLICK HERE TO PRINT SLIP</button>
            
            <div class="receipt-container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 26px;">THE LIFE CARE</h1>
                    <p style="margin: 5px 0; font-size: 14px;">MAJEED COLONY SEC 2, KARACHI</p>
                    <p style="margin: 2px 0; font-size: 15px; font-weight: bold;">Contact: {lab_phone}</p>
                    <div style="border: 1px solid #000; display: inline-block; padding: 2px 15px; margin-top: 10px; font-weight: bold;">
                        PATIENT RECEIPT
                    </div>
                </div>

                <table style="width: 100%; margin-top: 20px; font-size: 13px; line-height: 1.8;">
                    <tr>
                        <td width="55%"><b>Inv #:</b> {v[1]}</td>
                        <td align="right"><b>Date:</b> {v[2]}</td>
                    </tr>
                    <tr>
                        <td><b>Name:</b> {v[3]}</td>
                        <td align="right"><b>Age/Sex:</b> {v[5]}/{v[6]}</td>
                    </tr>
                    <tr>
                        <td><b>Mobile:</b> {v[4]}</td>
                        <td align="right"><b>Collected:</b> Lab</td>
                    </tr>
                    <tr>
                        <td colspan="2" style="border-top: 1px solid #f9f9f9; padding-top: 5px;">
                            <b>Ref By / Doctor:</b> {v[7]}
                        </td>
                    </tr>
                </table>

                <table style="width: 100%; margin-top: 15px; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 2px solid #000; border-top: 2px solid #000;">
                            <th align="left" style="padding: 8px 0;">Test Description</th>
                            <th align="right" style="padding: 8px 0;">Rate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {test_rows}
                    </tbody>
                </table>

                <div style="margin-top: 20px; border-top: 1px solid #000; padding-top: 10px;">
                    <table style="width: 100%; font-size: 15px; font-weight: bold;">
                        <tr><td>TOTAL BILL:</td><td align="right">Rs. {v[9]}</td></tr>
                        <tr style="color: #555;"><td>PAID AMOUNT:</td><td align="right">Rs. {v[10]}</td></tr>
                        <tr style="font-size: 18px; border-top: 1px dashed #000;">
                            <td style="padding-top: 8px;">BALANCE:</td>
                            <td align="right" style="padding-top: 8px;">Rs. {v[11]}</td>
                        </tr>
                    </table>
                </div>

                <div style="margin-top: 40px; text-align: center; font-size: 11px; border-top: 1px solid #eee; padding-top: 10px;">
                    <p style="margin: 2px 0;">This is a computer generated report.</p>
                    <p style="margin: 2px 0;"><b>Developed by Zain - 0370-2926075</b></p>
                </div>
            </div>
        </body>
        </html>
        """
        components.html(receipt_html, height=750, scrolling=True)

    except Exception as e:
        st.error(f"Error: {e}")
