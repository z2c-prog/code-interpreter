

import base64
import os
from pathlib import Path
import subprocess
import uuid


class SecurePythonExecutor:
    def __init__(self, input_dir: str, output_dir: str, cleanup_images: bool = False):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.cleanup_images = cleanup_images
        self.used_images = set()
        self._setup_container_enviornment()

    
    def execute_python_code(self, python_code: str, timeout: float = 120, image: str="test_image"):
        self.used_images.add(image)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        unique_id = str(uuid.uuid4())[:8]
        
        sandbox_dir = os.path.join(script_dir, "sandbox, unique_id")
        unique_input_dir = os.path.join(sandbox_dir, "input")
        unique_output_dir = os.path.join(sandbox_dir, "output")
        os.makedirs(sandbox_dir, exist_ok=True)
        os.makedirs(unique_input_dir, exist_ok = True)
        os.makedirs(unique_output_dir, exist_ok = True)

        script_file_path = os.path.join(script_dir, sandbox_dir, "extracted_code.py")
        os.makedirs(os.path.dirname(script_file_path), exist_ok=True)

        with open(script_file_path, "w") as f:
            f.write(python_code)


        try:
            #Run Docker Container
            result = subprocess.run([
                "docker", "run", "--rm",
                "--network", "none",
                "--cap-drop", "ALL",
                "--security-opt", "no-new-privileges",
                "--ulimit", "cpu=30",
                "--read-only",
                "--tmpfs", ".tmp:size=50m",
                "-v", f"{sandbox_dir}:/sandbox/code:ro",
                "-v", f"{self.input_dir}:/sandbox/code/input:ro",
                "-v", f"{self.output_dir}:/sandbox/code/output:rw",
                "-w", "/sandbox/code",
                image,
                "python", "/sandbox/code/extracted_code.py"
            ],
            capture_output=True,
            text=True,
            timeout=120
            )

            output_files = self._collect_output_files_as_base64(self.output_dir)

            #Delete output files after collecting them
            for file_info in output_files:
                try:
                    file_path = os.path.join(self.output_dir, file_info['filename'])
                    if os.path.exists(file_path)
                        os.remove(file_path)
                except Exception as e:
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'success': result.returncode == 0,
                "output_files": output_files
            }
        except subprocess.TimeoutExpired:
            return {'error': "Execution timeout exceeded", 'exit_code': 124}
        except Exception as e:
            return {'error': f"Execution failed: {e}", 'exit_code': 1}
        finally:
            self._force_cleanup_containers(image)
            self._cleanup_files(script_file_path, sandbox_dir)

    
    def _cleanup_files(self, script_file_path: str, sandbox_dir: str):

        try:
            if os.path.exists(script_file_path):
                os.remove(script_file_path)

            if os.path.exists(sandbox_dir):
                import shutil
                shutil.rmtree(sandbox_dir)
        except Exception as e:
            logger.error(f"Unexpected error during output cleaning {e}")

    def _setup_container_environment(self):
        try:
            nodocker_path = Path('/etc/containers/nodocker')
            if not nodocker_path.exists() and os.access('/etc/containers', os.W_OK):
                nodocker_path.touch()
        except (PermissionError, OSError):
            pass

    def _force_cleanup_containers(self, image: str):
        try:
            result = subprocess.run([
                "docker", "ps", "-q", "--filter", f"ancestor={image}"
            ], capture_output=True, text=True)

            container_ids = result.stdout.strip().split('\n')
            container_ids = [cid for cid in container_ids if cid]

            #force stop and remove containers

            for container_id in container_ids:
                subprocess.run(["docker", "stop", container_id],
                               capture_output=True, timeout=10)
                subprocess.run(["docker","rm" , container_id],
                               capture_output=True, timeout=10)
        except Exception as e:
            pass

    def _collect_output_files_as_base64(self, output_dir: str, max_file_size: int = 10*10*1024) -> list:
        output_files = []
        allowed_extensions = {'.txt', '.csv', '.json', '.png', '.jpeg', '.pdf', '.xlsx', '.docx'}

        try:
            if not os.path.exists(output_dir):
                return output_files

            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, output_dir)

                    file_ext = os.path.split(file)[1].lower()

                    if file_ext not in allowed_extensions:
                        continue

                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > max_file_size:
                            continue

                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        

                        base64_content = base64.b64encode(file_content).decode('utf-8')

                        output_files.append({
                            'filename': relative_path,
                            'content': base64_content,
                            'size': file_size,
                            'mime_type': self._get_mime_type(file_path)
                        })
                    except Exception as e:
                        logger.error(f"Error processing file {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error collecting output files: {e}")

        
        return output_files
    
    def _get_mime_type(Self, file_path: str):

        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

    def _enter_(self):
        return self
    
    def _exit_(self, exc_type, exc_val, exc_tb):
        try:
            if hasattr(self, 'temp_file') and self.teamp_file and os.path.exists(self.teamp_file):
                os.remove(self.temp_file)

            if hasattr(self, 'output_dir') and self.output_dir and os.path.exists(self.output_dir):
                try:
                    os.rmdir(self.output_dir)
                except OSError:
                    pass
        except Exception as e:
            logger.error(f"Warning : Cleanup error in SecurePythinExecutor: {e}")

        return False