#!/usr/bin/env python3


import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

try:
    from app.workflow import build_estimation_graph
except ModuleNotFoundError:
    print("\n" + "="*70)
    print("❌ ERROR: Virtual environment not activated")
    print("="*70)
    print("\nPlease activate the virtual environment first:")
    print("  source venv/bin/activate")
    print("\nThen run this script again:")
    print("  python show_workflow_graph.py")
    print("\n" + "="*70 + "\n")
    sys.exit(1)


def main():
    print("\n" + "="*70)
    print("GENERATING LANGGRAPH WORKFLOW VISUALIZATION")
    print("="*70 + "\n")
    
    try:
        # Build the graph
        app = build_estimation_graph()
        
        # Generate and save the graph
        graph = app.get_graph()
        png_data = graph.draw_mermaid_png()
        
        output_file = "workflow_graph.png"
        with open(output_file, "wb") as f:
            f.write(png_data)
        
        print(f"✅ Graph saved to: {output_file}")
        print(f"\nOpen with: open {output_file}")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure virtual environment is activated: source venv/bin/activate")
        print("  2. Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
