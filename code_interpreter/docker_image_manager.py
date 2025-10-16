

import os
import subprocess


class DockerImageManager:

        def __init__(self, image_name: str = "sogpt-python-sandbox"):
            self.image_name = image_name
        
        def build_image(self, force_rebuild: bool = False) -> bool:
            if not force_rebuild and self.image_exists():
                    return True
              
            script_dir = os.path.dirname(os.path.abspath(__file__))

            try:
                subprocess.run([
                      "docker", "build",
                      "-t", self.image_name,
                      script_dir
                ], check=True)

                return True
            
            except subprocess.CalledProcessError as e:
                  print(f"Failed to build image: {e}")
                  return False
            
        def image_exists(self) -> bool:
            try:
                result = subprocess.run([
                        "docker", "images", "-q", self.image_name
                ], capture_output=True, text=True)
                return bool(result.stdout.strip())
            except Exception as e:
                return False

        def remove_image(self) -> bool:
            try:
                subprocess.run([
                     "docker", "rmi", self.image_name
                ], check=True)
            except subprocess.CalledProcessError as e:
                 print(f"Exception while removing image: {e}")
                 return False
                  
