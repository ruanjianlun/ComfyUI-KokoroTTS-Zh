import os
import shutil
import sys


def copy_directory(source, destination):
    """
    Copy a directory and all its contents to a destination, excluding .git directory

    Args:
        source: Source directory path
        destination: Destination directory path
    """
    try:
        # Get the name of the source directory
        dir_name = os.path.basename(source)

        # Create the full destination path
        dest_path = os.path.join(destination, dir_name)

        # Check if destination already exists
        if os.path.exists(dest_path):
            print(f"警告: 目标路径 {dest_path} 已存在")
            choice = input("是否要覆盖? (y/n): ").lower()
            if choice != 'y':
                print("操作已取消")
                return False

            # Delete existing directory (excluding .git to avoid permission issues)
            print(f"正在删除现有目录内容: {dest_path}")
            for item in os.listdir(dest_path):
                item_path = os.path.join(dest_path, item)
                if item != '.git':
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
        else:
            # Create destination directory if it doesn't exist
            os.makedirs(dest_path)

        # Copy the directory with all contents except .git
        print(f"正在复制 {source} 到 {dest_path}")
        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(dest_path, item)
            if item != '.git':
                if os.path.isdir(s):
                    shutil.copytree(s, d, dirs_exist_ok=True)
                else:
                    shutil.copy2(s, d)

        print("复制完成!")
        return True

    except Exception as e:
        print(f"复制过程中出错: {str(e)}")
        return False


if __name__ == "__main__":
    # Source and destination paths
    source_dir = r"E:\work_space\python_work\comfyui_node_my\ComfyUI-KokoroTTS-Zh"
    dest_dir = r"E:\APP_install\ComfyUI\ComfyUI_windows_portable\ComfyUI\custom_nodes"

    # Check if source directory exists
    if not os.path.exists(source_dir):
        print(f"错误: 源目录 {source_dir} 不存在")
        sys.exit(1)

    # Check if destination directory exists
    if not os.path.exists(dest_dir):
        print(f"错误: 目标目录 {dest_dir} 不存在")
        sys.exit(1)

    # Copy the directory
    if copy_directory(source_dir, dest_dir):
        print("恭喜! ComfyUI-KokoroTTS-Zh 已成功复制到 ComfyUI 的自定义节点目录")
        print("您现在可以在 ComfyUI 中使用 KokoroTTS 节点了")
    else:
        print("复制失败，请检查错误信息并重试")
