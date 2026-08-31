import os
import shutil
from pathlib import Path

# Setup paths
BASE_DIR = Path("E:/tcs/dataset")
DS1_DIR = BASE_DIR / "1st/extract_folder/css-data"
DS2_DIR = BASE_DIR / "2nd/data/data"
FINAL_DIR = BASE_DIR / "final"

# 19 Class names
CLASS_NAMES = [
    "Person", "Helmet", "No helmet", "Gloves", "No gloves",
    "Boots", "No boots", "Glasses", "No glasses", "Safety vest",
    "No safety", "Face mask", "Face shield", "Mobile phone",
    "Tools", "Machine", "Machine guard", "Earmuffs", "Uniform"
]

# Maps local class IDs to the global 19-class IDs
# Dataset 1:
# 0: Hardhat, 1: Mask, 2: NO-Hardhat, 3: NO-Mask, 4: NO-Safety Vest, 
# 5: Person, 6: Safety Cone, 7: Safety Vest, 8: machinery, 9: vehicle
DS1_MAP = {
    0: 1,   # Hardhat -> Helmet
    1: 11,  # Mask -> Face mask
    2: 2,   # NO-Hardhat -> No helmet
    4: 10,  # NO-Safety Vest -> No safety
    5: 0,   # Person -> Person
    7: 9,   # Safety Vest -> Safety vest
    8: 15,  # machinery -> Machine
}

# Dataset 2:
# 0: smoking, 1: eating, 2: sleeping, 3: phone
DS2_MAP = {
    3: 13,  # phone -> Mobile phone
}

def create_dirs():
    for split in ["train", "val"]:
        (FINAL_DIR / "images" / split).mkdir(parents=True, exist_ok=True)
        (FINAL_DIR / "labels" / split).mkdir(parents=True, exist_ok=True)

def process_dataset(ds_dir, ds_map, prefix):
    # Mapping for splits: dataset 1 uses 'valid', dataset 2 uses 'val'
    splits = [("train", "train"), ("valid", "val"), ("val", "val")]
    
    for src_split, dst_split in splits:
        src_images = ds_dir / src_split / "images"
        src_labels = ds_dir / src_split / "labels"
        
        # Some datasets might not have images/labels subfolders, but put them directly in train/
        # Check if images/labels subfolders exist
        if not src_images.exists():
            src_images = ds_dir / src_split
            src_labels = ds_dir / src_split
            
        if not src_images.exists():
            continue
            
        dst_images = FINAL_DIR / "images" / dst_split
        dst_labels = FINAL_DIR / "labels" / dst_split

        for img_path in src_images.glob("*.*"):
            if img_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
                continue
                
            new_img_name = f"{prefix}_{img_path.name}"
            new_lbl_name = f"{prefix}_{img_path.stem}.txt"
            
            lbl_path = src_labels / f"{img_path.stem}.txt"
            
            # If label file exists, parse it and copy
            if lbl_path.exists():
                new_lines = []
                with open(lbl_path, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            cls_id = int(parts[0])
                            if cls_id in ds_map:
                                new_cls_id = ds_map[cls_id]
                                new_line = f"{new_cls_id} {' '.join(parts[1:])}\n"
                                new_lines.append(new_line)
                
                # Only copy image and label if there is at least one valid object
                if len(new_lines) > 0:
                    shutil.copy(img_path, dst_images / new_img_name)
                    with open(dst_labels / new_lbl_name, "w") as f:
                        f.writelines(new_lines)

def write_yaml():
    yaml_content = f"path: E:/tcs/dataset/final\n"
    yaml_content += "train: images/train\n"
    yaml_content += "val: images/val\n\n"
    yaml_content += "names:\n"
    for i, name in enumerate(CLASS_NAMES):
        yaml_content += f"  {i}: {name}\n"
        
    with open(FINAL_DIR / "data.yaml", "w") as f:
        f.write(yaml_content)

if __name__ == "__main__":
    print("Creating directories...")
    create_dirs()
    
    print("Processing Dataset 1...")
    if DS1_DIR.exists():
        process_dataset(DS1_DIR, DS1_MAP, "ds1")
    else:
        print(f"Warning: {DS1_DIR} not found.")
        
    print("Processing Dataset 2...")
    if DS2_DIR.exists():
        process_dataset(DS2_DIR, DS2_MAP, "ds2")
    else:
        print(f"Warning: {DS2_DIR} not found.")
        
    print("Writing data.yaml...")
    write_yaml()
    
    print("Merge Complete!")
