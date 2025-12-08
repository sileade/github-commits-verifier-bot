#!/usr/bin/env python3
"""
Test Local LLM Setup
Проверыть инсталляцию Ollama
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from local_analyzer import LocalAnalyzer


async def main():
    print("\n🤖 Testing Local LLM Setup...\n")
    
    # Initialize
    print("1. Initializing LocalAnalyzer...")
    try:
        analyzer = LocalAnalyzer(
            ollama_host="http://localhost:11434",
            model="mistral"
        )
        print("   ✓ LocalAnalyzer created\n")
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
        return False
    
    # Check health
    print("2. Checking Ollama health...")
    health = await analyzer.check_ollama_health()
    if health:
        print("   ✓ Ollama is running and model is available\n")
    else:
        print("   ✗ Ollama not available\n")
        print("   Setup Ollama with:")
        print("   docker pull ollama/ollama")
        print("   docker run -d -p 11434:11434 -v ollama:/root/.ollama ollama/ollama")
        print("   docker exec ollama ollama pull mistral\n")
        return False
    
    # Test analysis
    print("3. Testing commit analysis...")
    
    test_diff = """--- a/bot.py
+++ b/bot.py
@@ -1,3 +1,5 @@
#!/usr/bin/env python3
+# Add better error handling
+import logging
 
 def handle_user_input():
"""
    
    test_message = "Add logging support for better debugging"
    
    print("   Analyzing... (this may take 10-30 seconds)\n")
    
    analysis = await analyzer.analyze_diff(test_diff, test_message)
    
    if analysis:
        print("   ✓ Analysis completed!\n")
        print("   Results:")
        print(f"   - Summary: {analysis.get('summary', 'N/A')}")
        print(f"   - Impact: {analysis.get('impact', 'N/A')}")
        print(f"   - Strengths: {analysis.get('strengths', 'N/A')}")
        print(f"   - Concerns: {analysis.get('concerns', 'N/A')}")
        print(f"   - Recommendation: {analysis.get('recommendation', 'N/A')}\n")
        return True
    else:
        print("   ✗ Analysis failed\n")
        return False


if __name__ == "__main__":
    print("╔" + "="*60 + "╗")
    print("║" + " Local LLM (Ollama) Setup Test ".center(60) + "║")
    print("╚" + "="*60 + "╝")
    
    try:
        success = asyncio.run(main())
        if success:
            print("🌟 Local LLM setup is working!\n")
            print("Your bot now has free, private AI analysis.\n")
            sys.exit(0)
        else:
            print("⚠️ Setup check failed. See instructions above.\n")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n⚠️ Error: {e}\n")
        sys.exit(1)
