import os

def remove_pro_from_files():
    # List of files to process
    files_to_update = [
        'README.md',
        'README.en.md',
        'README.zh.md',
        'AI_INTEGRATION_GUIDE.md',
        'core/settings.json',
        'core/static/main.js',
        'core/templates/index.html',
        'core/templates/results.html',
        'core/templates/settings.html'
    ]
    
    for file_path in files_to_update:
        full_path = f'd:/Armando/Desktop/workSpace/ProyectosDev/searXena/{file_path}'
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace "searXena Pro" with "searXena"
            new_content = content.replace('searXena Pro', 'searXena')
            
            if content != new_content:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {file_path}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    remove_pro_from_files()
