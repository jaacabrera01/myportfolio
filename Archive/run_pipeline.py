"""
Master pipeline to execute all analysis notebooks in sequence.

Usage:
    python run_pipeline.py
    python run_pipeline.py --skip-eda  # Skip EDA step
"""

import subprocess
import sys
import os
from datetime import datetime
import argparse

def run_notebook(notebook_path, timeout=3600):
    """Execute Jupyter notebook using nbconvert"""
    print(f"\n{'='*80}")
    print(f"Executing: {notebook_path}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run([
            'jupyter', 'nbconvert',
            '--to', 'notebook',
            '--execute',
            '--inplace',
            '--ExecutePreprocessor.timeout={}'.format(timeout),
            notebook_path
        ], check=True, capture_output=True, text=True)
        
        print(f"✅ {notebook_path} completed successfully")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"❌ {notebook_path} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run analysis pipeline')
    parser.add_argument('--skip-eda', action='store_true', help='Skip EDA step')
    parser.add_argument('--skip-regression', action='store_true', help='Skip regression')
    parser.add_argument('--skip-classification', action='store_true', help='Skip classification')
    args = parser.parse_args()
    
    # Define pipeline
    notebooks = []
    
    if not args.skip_eda:
        notebooks.append('01_EDA_Analysis.ipynb')
    if not args.skip_regression:
        notebooks.append('02_Regression_Benchmark_25Methods.ipynb')
    if not args.skip_classification:
        notebooks.append('03_Classification_Benchmark_Complete.ipynb')
    
    # Create output directory
    os.makedirs('outputs', exist_ok=True)
    
    # Log file
    log_file = f'outputs/pipeline_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    
    print(f"{'='*80}")
    print(f"ANALYSIS PIPELINE")
    print(f"{'='*80}")
    print(f"Log file: {log_file}")
    print(f"Notebooks to execute: {len(notebooks)}")
    
    # Execute notebooks
    results = {}
    for notebook in notebooks:
        if not os.path.exists(notebook):
            print(f"⚠️  {notebook} not found, skipping...")
            results[notebook] = False
            continue
        
        success = run_notebook(notebook)
        results[notebook] = success
        
        # Log result
        with open(log_file, 'a') as f:
            status = "SUCCESS" if success else "FAILED"
            f.write(f"{datetime.now()}: {notebook} - {status}\n")
        
        if not success:
            print(f"\n⚠️  Stopping pipeline due to failure in {notebook}")
            break
    
    # Final summary
    print(f"\n{'='*80}")
    print("PIPELINE SUMMARY")
    print(f"{'='*80}")
    for notebook, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {notebook}")
    
    all_success = all(results.values())
    if all_success:
        print("\n✅ All notebooks executed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some notebooks failed. Check log file for details.")
        sys.exit(1)

if __name__ == '__main__':
    main()
