import sys
import os
import subprocess


ROOT = os.path.dirname(__file__)
REQUIREMENTS = os.path.join(ROOT, 'requirements.txt')


def main():
    print('Update pip and setuptools')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools'])

    print('Install requirements')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS])
    
    print('Install PyTorch with CUDA support')
    subprocess.run([sys.executable, '-m', 'pip', 'install',
                    'torch==1.8.0+cu111',
                    'torchvision==0.9.0+cu111',
                    'torchaudio===0.8.0',
                    '-f', 'https://download.pytorch.org/whl/torch_stable.html'])
                    
    print('Installed successfully!')
    
    
if __name__ == '__main__':
    main()
