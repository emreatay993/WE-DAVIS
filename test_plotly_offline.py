"""
Test script to verify Plotly works offline.
Run this AFTER building with PyInstaller and BEFORE transferring to offline network.

Usage:
1. Build the executable: build_offline.bat
2. Disconnect from internet
3. Run: python test_plotly_offline.py
4. If successful, plots will open in browser and work correctly
"""

import sys
import os
import tempfile
import webbrowser
import plotly.graph_objects as go
import plotly.io as pio

def test_plotly_inline():
    """Test that Plotly can generate HTML with inline JavaScript."""
    print("=" * 60)
    print("Testing Plotly Offline Functionality")
    print("=" * 60)
    print()
    
    # Create a simple figure
    print("1. Creating test figure...")
    fig = go.Figure(data=[
        go.Scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], name='Test Data')
    ])
    fig.update_layout(title="Offline Plotly Test", xaxis_title="X Axis", yaxis_title="Y Axis")
    print("   ✓ Figure created")
    print()
    
    # Generate HTML with inline plotly.js
    print("2. Generating HTML with inline Plotly.js...")
    try:
        html_content = pio.to_html(
            fig, 
            full_html=True, 
            include_plotlyjs=True,  # This should inline the entire plotly.min.js
            config={'responsive': True}
        )
        print("   ✓ HTML generated successfully")
        print()
    except Exception as e:
        print(f"   ✗ FAILED: {e}")
        print()
        return False
    
    # Check if plotly.js is actually embedded
    print("3. Verifying plotly.js is embedded in HTML...")
    if 'Plotly' in html_content and len(html_content) > 100000:  # plotly.min.js is large
        print(f"   ✓ Plotly.js is embedded (HTML size: {len(html_content):,} bytes)")
        print()
    else:
        print("   ✗ WARNING: Plotly.js may not be fully embedded")
        print(f"   HTML size: {len(html_content):,} bytes (expected > 100,000)")
        print()
        return False
    
    # Save to temp file and open
    print("4. Opening plot in browser...")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_path = f.name
    
    print(f"   ✓ Saved to: {temp_path}")
    print()
    
    # Open in browser
    try:
        webbrowser.open('file://' + os.path.abspath(temp_path))
        print("   ✓ Opened in browser")
        print()
    except Exception as e:
        print(f"   ✗ Could not open browser: {e}")
        print(f"   Please open this file manually: {temp_path}")
        print()
    
    print("=" * 60)
    print("TEST RESULT: SUCCESS")
    print("=" * 60)
    print()
    print("If the plot displays correctly in your browser,")
    print("then the offline functionality is working!")
    print()
    print("You can now:")
    print("1. Build the executable with build_offline.bat")
    print("2. Transfer dist\\WE-DAVIS\\ to your offline network")
    print("3. Run WE-DAVIS.exe on the offline system")
    print()
    
    return True

def check_plotly_resources():
    """Check if plotly's JavaScript resources are accessible."""
    print("Checking Plotly package resources...")
    print()
    
    try:
        # Check if plotly can find its bundled JS
        import plotly
        plotly_path = os.path.dirname(plotly.__file__)
        print(f"Plotly package location: {plotly_path}")
        
        # Look for package_data or similar
        package_data_path = os.path.join(plotly_path, 'package_data')
        if os.path.exists(package_data_path):
            print(f"✓ Package data folder found: {package_data_path}")
            
            # List some contents
            try:
                contents = os.listdir(package_data_path)
                print(f"  Contains {len(contents)} items")
            except:
                pass
        else:
            print(f"Note: Standard package_data folder not found (this is OK)")
            print(f"      Plotly may store resources differently")
        
        print()
        
    except Exception as e:
        print(f"Warning: Could not check package resources: {e}")
        print()

if __name__ == "__main__":
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        WE-DAVIS Plotly Offline Functionality Test         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    # Check resources
    check_plotly_resources()
    
    # Run test
    try:
        success = test_plotly_inline()
        if success:
            sys.exit(0)
        else:
            print("TEST FAILED - See errors above")
            sys.exit(1)
    except Exception as e:
        print()
        print("=" * 60)
        print("TEST RESULT: FAILED")
        print("=" * 60)
        print()
        print(f"Error: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


