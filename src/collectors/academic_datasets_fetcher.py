from __future__ import annotations

import json
import time
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .acquisition_logger import AcquisitionLogger


@dataclass
class AcademicDatasetsFetcher:
    data_dir: Path
    rate_limit_sleep: float = 3.0

    @property
    def raw_dir(self) -> Path:
        p = self.data_dir / "raw" / "academic_datasets"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _download_file(self, url: str, output_path: Path, chunk_size: int = 8192) -> bool:
        """Download a file with progress indication"""
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "DSATrain-AcademicFetcher/0.1 (Educational Research)",
                    "Accept": "*/*"
                }
            )
            
            with urllib.request.urlopen(req, timeout=60) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with output_path.open("wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownloading {output_path.name}: {percent:.1f}%", end="", flush=True)
                
                print()  # New line after progress
                return True
                
        except Exception as e:
            print(f"\n❌ Failed to download {url}: {e}")
            return False

    def fetch_codecomplex_dataset(self) -> Dict[str, Any]:
        """Fetch the CodeComplex dataset for time complexity analysis"""
        print("=== Fetching CodeComplex Dataset ===")
        
        codecomplex_dir = self.raw_dir / "codecomplex"
        codecomplex_dir.mkdir(exist_ok=True)
        
        # GitHub repository data
        # Note: The actual dataset files need to be downloaded from the research paper's supplementary materials
        # For now, we'll create placeholder metadata and download instructions
        
        codecomplex_info = {
            "dataset_name": "CodeComplex",
            "description": "Time complexity annotations for Java and Python programs from Codeforces",
            "paper_url": "https://arxiv.org/html/2401.08719v1",
            "github_url": "https://github.com/sybaik1/CodeComplex-Models",
            "total_samples": 9800,
            "languages": ["Java", "Python"],
            "complexity_classes": ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n²)", "O(n³)", "O(2ⁿ)"],
            "annotation_method": "Expert manual annotation",
            "source_problems": "Codeforces competitive programming platform"
        }
        
        # Create metadata file
        metadata_file = codecomplex_dir / "dataset_metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(codecomplex_info, f, ensure_ascii=False, indent=2)
        
        # Create instructions for manual download
        instructions_file = codecomplex_dir / "download_instructions.md"
        instructions = """# CodeComplex Dataset Download Instructions

The CodeComplex dataset contains 9,800 expertly annotated code samples with time complexity labels.

## Manual Download Required

Due to the dataset being distributed through academic channels, manual download is required:

1. **Paper**: https://arxiv.org/html/2401.08719v1
2. **GitHub**: https://github.com/sybaik1/CodeComplex-Models
3. **Contact**: Check the paper for dataset availability or contact authors

## Expected Files

- `codecomplex_java.json` - Java code samples with complexity annotations
- `codecomplex_python.json` - Python code samples with complexity annotations
- `metadata.json` - Dataset statistics and annotation guidelines

## Integration

Once downloaded, place the files in this directory. The standardizer will automatically process them.
"""
        
        with instructions_file.open("w", encoding="utf-8") as f:
            f.write(instructions)
        
        print(f"✅ Created metadata and instructions in: {codecomplex_dir}")
        return {
            "dataset": "codecomplex",
            "status": "metadata_created",
            "requires_manual_download": True,
            "metadata_file": str(metadata_file),
            "instructions_file": str(instructions_file)
        }

    def fetch_py_ast_dataset(self) -> Dict[str, Any]:
        """Fetch the py_ast dataset from Hugging Face"""
        print("=== Fetching py_ast Dataset Info ===")
        
        py_ast_dir = self.raw_dir / "py_ast"
        py_ast_dir.mkdir(exist_ok=True)
        
        # Hugging Face dataset info
        py_ast_info = {
            "dataset_name": "py_ast",
            "description": "150,000 Abstract Syntax Trees from Python programs on GitHub",
            "huggingface_url": "https://huggingface.co/datasets/1stvamp/py_ast",
            "total_samples": 150000,
            "format": "JSON with AST representations",
            "license": "MIT/BSD (GitHub repositories)",
            "paper_reference": "AST-T5: Structure-Aware Pretraining for Code Generation and Understanding",
            "use_case": "Training models for structural code understanding"
        }
        
        # Create metadata file
        metadata_file = py_ast_dir / "dataset_metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(py_ast_info, f, ensure_ascii=False, indent=2)
        
        # Create Hugging Face download instructions
        instructions_file = py_ast_dir / "huggingface_download.py"
        download_script = '''"""
Download script for py_ast dataset from Hugging Face
Requires: pip install datasets
"""

from datasets import load_dataset
import json
from pathlib import Path

def download_py_ast():
    print("Loading py_ast dataset from Hugging Face...")
    
    # Load the dataset
    dataset = load_dataset("1stvamp/py_ast")
    
    # Save to local files
    output_dir = Path(__file__).parent
    
    for split_name, split_data in dataset.items():
        output_file = output_dir / f"py_ast_{split_name}.jsonl"
        
        print(f"Saving {split_name} split to {output_file}")
        with output_file.open("w", encoding="utf-8") as f:
            for example in split_data:
                f.write(json.dumps(example) + "\\n")
        
        print(f"✅ Saved {len(split_data)} examples to {output_file}")

if __name__ == "__main__":
    download_py_ast()
'''
        
        with instructions_file.open("w", encoding="utf-8") as f:
            f.write(download_script)
        
        print(f"✅ Created metadata and download script in: {py_ast_dir}")
        return {
            "dataset": "py_ast",
            "status": "download_script_created",
            "requires_huggingface_datasets": True,
            "metadata_file": str(metadata_file),
            "download_script": str(instructions_file)
        }

    def fetch_ml4code_dataset_index(self) -> Dict[str, Any]:
        """Fetch the ml4code dataset collection index"""
        print("=== Fetching ml4code Dataset Collection ===")
        
        ml4code_dir = self.raw_dir / "ml4code"
        ml4code_dir.mkdir(exist_ok=True)
        
        # Try to fetch the repository index
        github_api_url = "https://api.github.com/repos/CUHK-ARISE/ml4code-dataset"
        
        try:
            req = urllib.request.Request(
                github_api_url,
                headers={
                    "User-Agent": "DSATrain-AcademicFetcher/0.1",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                repo_info = json.loads(response.read().decode("utf-8"))
            
            print(f"✅ Fetched repository info: {repo_info['full_name']}")
            
        except Exception as e:
            print(f"⚠️ Could not fetch GitHub API info: {e}")
            repo_info = {
                "name": "ml4code-dataset",
                "description": "A collection of datasets for machine learning for code",
                "html_url": "https://github.com/CUHK-ARISE/ml4code-dataset"
            }
        
        # Create comprehensive dataset index based on research document
        ml4code_index = {
            "collection_name": "ml4code-dataset",
            "description": "Meta-collection of academic datasets for code analysis",
            "repository_url": "https://github.com/CUHK-ARISE/ml4code-dataset",
            "total_datasets": "50+",
            "categories": {
                "bug_detection": [
                    "OOPSLA19Li",
                    "Devign", 
                    "Draper",
                    "Big-Vul"
                ],
                "code_classification": [
                    "POJ-104",
                    "OJ Clone Detection"
                ],
                "clone_detection": [
                    "BigCloneBench"
                ],
                "vulnerability_analysis": [
                    "CVE-based datasets",
                    "Security patch datasets"
                ],
                "code_generation": [
                    "HumanEval variants",
                    "CodeContest"
                ]
            },
            "languages_covered": ["C", "C++", "Java", "Python", "JavaScript"],
            "typical_sizes": "Millions of functions",
            "annotation_types": [
                "Static analysis labels",
                "Expert annotations",
                "Automated tool outputs"
            ]
        }
        
        # Save repository info
        repo_file = ml4code_dir / "repository_info.json"
        with repo_file.open("w", encoding="utf-8") as f:
            json.dump(repo_info, f, ensure_ascii=False, indent=2)
        
        # Save dataset index
        index_file = ml4code_dir / "dataset_index.json"
        with index_file.open("w", encoding="utf-8") as f:
            json.dump(ml4code_index, f, ensure_ascii=False, indent=2)
        
        # Create exploration instructions
        instructions_file = ml4code_dir / "exploration_guide.md"
        instructions = """# ml4code Dataset Collection Exploration

This collection contains 50+ academic datasets for machine learning on code.

## Key Datasets for DSATrain

### High Priority - Code Quality Analysis
1. **Bug Detection Datasets**
   - OOPSLA19Li: Labeled buggy vs non-buggy functions
   - Devign: Graph-based vulnerability detection
   - Big-Vul: Large-scale vulnerability dataset

2. **Code Clone Detection**
   - BigCloneBench: Semantic code clone pairs
   - POJ-104: Programming contest problem classification

### Integration Steps

1. **Browse Repository**: https://github.com/CUHK-ARISE/ml4code-dataset
2. **Select Datasets**: Choose 3-5 most relevant for code evaluation
3. **Download**: Follow individual dataset instructions
4. **Standardize**: Convert to common format for training

### Recommended Selection Criteria
- Focus on Python/Java datasets (matches our problem sources)
- Prioritize function-level analysis (matches interview scope)
- Select datasets with clear quality labels
"""
        
        with instructions_file.open("w", encoding="utf-8") as f:
            f.write(instructions)
        
        print(f"✅ Created index and exploration guide in: {ml4code_dir}")
        return {
            "dataset": "ml4code_collection",
            "status": "index_created",
            "total_datasets": "50+",
            "repo_file": str(repo_file),
            "index_file": str(index_file),
            "guide_file": str(instructions_file)
        }

    def fetch_code_metrics_datasets(self) -> Dict[str, Any]:
        """Fetch code metrics datasets from various sources"""
        print("=== Fetching Code Metrics Datasets ===")
        
        metrics_dir = self.raw_dir / "code_metrics"
        metrics_dir.mkdir(exist_ok=True)
        
        # Kaggle code metrics dataset
        code_metrics_info = {
            "dataset_name": "Code Metrics Software Project Structure",
            "description": "Software metrics for code quality assessment",
            "kaggle_url": "https://www.kaggle.com/datasets/amalsalilan/code-metrics-dataset-softwareprojectstructure",
            "metrics_included": [
                "Cyclomatic Complexity",
                "Lines of Code (LOC)",
                "Coupling Between Objects (CBO)",
                "Lack of Cohesion in Methods (LCOM)",
                "Depth of Inheritance Tree (DIT)",
                "Number of Children (NOC)"
            ],
            "use_case": "Quantitative code quality assessment for interview evaluation"
        }
        
        # Save metadata
        metadata_file = metrics_dir / "code_metrics_metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(code_metrics_info, f, ensure_ascii=False, indent=2)
        
        # Create Kaggle download instructions
        instructions_file = metrics_dir / "kaggle_download_instructions.md"
        instructions = """# Code Metrics Dataset Download

## Kaggle Dataset
- **URL**: https://www.kaggle.com/datasets/amalsalilan/code-metrics-dataset-softwareprojectstructure
- **Requirements**: Kaggle account and API credentials

## Download Steps
1. Install Kaggle CLI: `pip install kaggle`
2. Set up API credentials: https://www.kaggle.com/docs/api
3. Download: `kaggle datasets download -d amalsalilan/code-metrics-dataset-softwareprojectstructure`

## Expected Files
- `software_metrics.csv` - Quantitative code quality metrics
- `project_structure.csv` - Project organization metrics

## Integration
These metrics will be used to train models for objective code quality assessment.
"""
        
        with instructions_file.open("w", encoding="utf-8") as f:
            f.write(instructions)
        
        print(f"✅ Created code metrics info in: {metrics_dir}")
        return {
            "dataset": "code_metrics",
            "status": "instructions_created",
            "source": "kaggle",
            "metadata_file": str(metadata_file),
            "instructions_file": str(instructions_file)
        }

    def run_acquisition(self) -> Dict[str, Any]:
        """Run complete academic datasets acquisition"""
        logger = AcquisitionLogger(self.data_dir)
        
        try:
            print("=== Academic Code Quality Datasets Acquisition ===")
            
            results = []
            
            # Fetch each dataset type
            results.append(self.fetch_codecomplex_dataset())
            time.sleep(self.rate_limit_sleep)
            
            results.append(self.fetch_py_ast_dataset())
            time.sleep(self.rate_limit_sleep)
            
            results.append(self.fetch_ml4code_dataset_index())
            time.sleep(self.rate_limit_sleep)
            
            results.append(self.fetch_code_metrics_datasets())
            
            # Save acquisition summary
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = self.raw_dir / f"academic_datasets_summary_{ts}.json"
            
            summary = {
                "timestamp": datetime.now().isoformat(),
                "total_datasets": len(results),
                "datasets_prepared": len([r for r in results if r["status"] in ["metadata_created", "index_created", "instructions_created", "download_script_created"]]),
                "results": results,
                "next_steps": [
                    "Review individual dataset instructions",
                    "Download datasets requiring manual acquisition",
                    "Run Hugging Face download scripts",
                    "Standardize formats for training pipeline"
                ]
            }
            
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            meta = {
                "timestamp": datetime.now().isoformat(),
                "datasets_prepared": len(results),
                "output_file": str(summary_file)
            }
            
            logger.log("academic_datasets", "metadata_preparation", 
                      records=len(results), success=True, metadata=meta)
            
            return meta
            
        except Exception as e:
            logger.log("academic_datasets", "metadata_preparation", 
                      records=0, success=False, error=str(e))
            raise
