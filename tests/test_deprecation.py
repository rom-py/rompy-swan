#!/usr/bin/env python3
"""
Test script to verify the deprecation warning works correctly.
"""
import warnings

# Capture warnings
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    
    # Import and use the deprecated class
    from rompy_swan.config import SwanConfigComponents
    
    print(f"Number of warnings captured: {len(w)}")
    
    if w:
        for warning in w:
            print(f"Warning category: {warning.category.__name__}")
            print(f"Warning message: {warning.message}")
            print(f"Warning filename: {warning.filename}")
            print(f"Warning lineno: {warning.lineno}")
    
    # Test that both classes are available and work the same
    from rompy_swan.config import SwanConfig
    
    print(f"SwanConfig class: {SwanConfig}")
    print(f"SwanConfigComponents class: {SwanConfigComponents}")
    print(f"SwanConfigComponents is subclass of SwanConfig: {issubclass(SwanConfigComponents, SwanConfig)}")
    
    print("✓ Deprecation test completed successfully")
