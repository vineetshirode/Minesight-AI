import os
import shutil
import subprocess

def run_cmd(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode != 0:
        print(f"[CMD WARN/ERR] {cmd}\n  stderr: {p.stderr.strip()}\n  stdout: {p.stdout.strip()}")
    return p.returncode == 0

def git_move_or_shutil(src, dst):
    if not os.path.exists(src):
        print(f"[SKIP] Source does not exist: {src}")
        return False
    dst_dir = os.path.dirname(dst)
    if dst_dir and not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    
    # Try git mv first
    success = run_cmd(f'git mv "{src}" "{dst}"')
    if not success:
        print(f"[FALLBACK] Using shutil.move for {src} -> {dst}")
        shutil.move(src, dst)
        run_cmd(f'git add "{dst}"')
    return True

print("=== STARTING REPOSITORY REORGANIZATION ===")

# 1. Create target folders
target_dirs = [
    "data",
    "backend",
    "tests",
    "docs",
    "scripts",
    "notebooks",
    "outputs",
    "_archive"
]
for d in target_dirs:
    os.makedirs(d, exist_ok=True)

# 2. Rename model_1-master -> model_1
if os.path.exists("model_1-master"):
    # If nested venv exists, delete it first so git mv won't complain about untracked files
    if os.path.exists("model_1-master/venv"):
        shutil.rmtree("model_1-master/venv", ignore_errors=True)
    git_move_or_shutil("model_1-master", "model_1")
    print("[DONE] Renamed model_1-master -> model_1")

# 3. Rename model_2-master -> model_2
if os.path.exists("model_2-master"):
    git_move_or_shutil("model_2-master", "model_2")
    print("[DONE] Renamed model_2-master -> model_2")

# Create model_2/audit and move audit files
os.makedirs("model_2/audit", exist_ok=True)
audit_files = [
    "AUDIT_REPORT.txt",
    "CHECK5_DEEP_ANALYSIS.py",
    "FINAL_MODEL_SELECTION_AUDIT.py",
    "FINAL_VERDICT.txt",
    "LEAKAGE_AUDIT.py",
    "QUICK_REFERENCE.txt",
    "audit_output.txt"
]
for f in audit_files:
    src_f = os.path.join("model_2", f)
    dst_f = os.path.join("model_2", "audit", f)
    if os.path.exists(src_f):
        git_move_or_shutil(src_f, dst_f)
print("[DONE] Organized model_2/audit/")

# 4. Move raw data to data/
data_files = [
    "manganese_occurrences_MOIL_study_area.csv",
    "manganese_occurrences_SIH26009.csv",
    "manganese_production_dataset (1).csv",
    "manganese_production_prototype_v2.csv"
]
for f in data_files:
    if os.path.exists(f):
        git_move_or_shutil(f, os.path.join("data", f))
print("[DONE] Populated data/")

# 5. Move backend/server.py and setup root shim
# We'll copy server.py to backend/server.py and create root server.py
if os.path.exists("server.py"):
    shutil.copy2("server.py", "backend/server.py")
    run_cmd('git add "backend/server.py"')
with open("backend/__init__.py", "w") as f:
    pass
run_cmd('git add "backend/__init__.py"')
print("[DONE] Created backend/server.py & backend/__init__.py")

# 6. Move tests/test_simulator_api.py
if os.path.exists("test_simulator_api.py"):
    git_move_or_shutil("test_simulator_api.py", "tests/test_simulator_api.py")
with open("tests/__init__.py", "w") as f:
    pass
run_cmd('git add "tests/__init__.py"')
print("[DONE] Created tests/test_simulator_api.py & tests/__init__.py")

# 7. Move docs/
if os.path.exists("MODEL1_DATA_QUALITY_REPORT.md"):
    git_move_or_shutil("MODEL1_DATA_QUALITY_REPORT.md", "docs/MODEL1_DATA_QUALITY_REPORT.md")
print("[DONE] Moved docs/MODEL1_DATA_QUALITY_REPORT.md")

# 8. Move scripts/
if os.path.exists("model1_pipeline.py"):
    git_move_or_shutil("model1_pipeline.py", "scripts/model1_pipeline.py")
print("[DONE] Moved scripts/model1_pipeline.py")

# 9. Move notebooks/
if os.path.exists("mvp.ipynb"):
    git_move_or_shutil("mvp.ipynb", "notebooks/mvp.ipynb")
print("[DONE] Moved notebooks/mvp.ipynb")

# 10. Move output/ -> outputs/
if os.path.exists("output"):
    for f in os.listdir("output"):
        src = os.path.join("output", f)
        dst = os.path.join("outputs", f)
        git_move_or_shutil(src, dst)
    if os.path.exists("output") and not os.listdir("output"):
        os.rmdir("output")
print("[DONE] Moved output/ -> outputs/")

# 11. Move archive files
archive_items = [
    "pdf",
    "model1_spatial_features.csv",
    "model1_spatial_features.geojson",
    os.path.join("dashboard", "generate_dashboard_data.py")
]
for item in archive_items:
    if os.path.exists(item):
        dst = os.path.join("_archive", os.path.basename(item))
        git_move_or_shutil(item, dst)
print("[DONE] Populated _archive/")

print("\n=== REORGANIZATION PASS COMPLETED ===")
