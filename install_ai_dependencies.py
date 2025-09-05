#!/usr/bin/env python3
"""
AI Dependencies Installation Script for Label Maker
This script helps install the necessary AI packages for enhanced JSON matching.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors gracefully."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e}")
        if e.stdout:
            print(f"  Output: {e.stdout}")
        if e.stderr:
            print(f"  Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required for AI dependencies")
        print(f"  Current version: {sys.version}")
        return False
    print(f"✓ Python version {sys.version.split()[0]} is compatible")
    return True

def install_ai_dependencies():
    """Install AI dependencies for enhanced matching."""
    print("🚀 Installing AI Dependencies for Enhanced JSON Matching")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Upgrade pip first
    if not run_command("pip install --upgrade pip", "Upgrading pip"):
        print("Warning: pip upgrade failed, continuing anyway...")
    
    # Install core AI packages
    packages = [
        ("sentence-transformers", "AI-powered semantic similarity"),
        ("torch", "PyTorch deep learning framework"),
        ("transformers", "Hugging Face transformers library"),
        ("numpy", "Numerical computing"),
        ("scikit-learn", "Machine learning utilities"),
    ]
    
    for package, description in packages:
        if not run_command(f"pip install {package}", f"Installing {package} ({description})"):
            return False
    
    # Install optional text processing packages
    optional_packages = [
        ("spacy", "Advanced text processing"),
        ("nltk", "Natural language toolkit"),
    ]
    
    print("\n📦 Installing optional text processing packages...")
    for package, description in optional_packages:
        try:
            run_command(f"pip install {package}", f"Installing {package} ({description})")
        except:
            print(f"Warning: {package} installation failed, continuing...")
    
    # Download spacy model if available
    try:
        run_command("python -m spacy download en_core_web_sm", "Downloading English language model for spaCy")
    except:
        print("Warning: spaCy model download failed, continuing...")
    
    # Download NLTK data
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        print("✓ NLTK data downloaded successfully")
    except:
        print("Warning: NLTK data download failed, continuing...")
    
    print("\n🎉 AI Dependencies Installation Complete!")
    print("\nThe following AI-enhanced features are now available:")
    print("• Semantic similarity matching for vendors and brands")
    print("• Context-aware product matching")
    print("• AI-powered confidence scoring")
    print("• Enhanced vendor matching with semantic understanding")
    
    return True

def test_ai_installation():
    """Test if AI dependencies are working correctly."""
    print("\n🧪 Testing AI Installation...")
    
    try:
        # Test sentence-transformers
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ sentence-transformers working correctly")
        
        # Test basic functionality
        text1 = "dank czar"
        text2 = "dcz holdings inc"
        embeddings = model.encode([text1, text2])
        print("✓ Semantic embeddings generated successfully")
        
        # Test numpy
        import numpy as np
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        print(f"✓ Similarity calculation working: {similarity:.3f}")
        
        print("\n🎯 AI Installation Test Passed!")
        return True
        
    except Exception as e:
        print(f"✗ AI Installation Test Failed: {e}")
        return False

if __name__ == "__main__":
    print("Label Maker - AI Dependencies Installer")
    print("=" * 40)
    
    # Install dependencies
    if install_ai_dependencies():
        # Test installation
        if test_ai_installation():
            print("\n✅ All AI dependencies are installed and working correctly!")
            print("\nYou can now use AI-enhanced JSON matching with:")
            print("• Better vendor matching using semantic similarity")
            print("• Improved brand matching with AI confidence scoring")
            print("• Context-aware product matching")
        else:
            print("\n⚠️  Dependencies installed but test failed. Check error messages above.")
    else:
        print("\n❌ Installation failed. Please check the error messages above.")
        sys.exit(1)
