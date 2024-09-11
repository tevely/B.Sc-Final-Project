set -e
MATLAB_SRC=./matlab_src
REVISION=f565044712ac3a20526c2dd52acd509663d1786d
cd ${MATLAB_SRC}
if [ ! -d BPM-Matlab ]
then
    echo "Cloning BPM-Matlab to ${MATLAB_SRC}"
    git clone https://github.com/ankrh/BPM-Matlab.git
    cd BPM-Matlab
else
    echo "Found BPM-Matlab in ${MATLAB_SRC}"
    cd BPM-Matlab
    git checkout Release
    git pull origin Release
fi
git checkout $REVISION .
echo "Applying patch"
git apply ../BPM-Matlab-make-modes-writable.patch
git apply ../BPM-Matlab-disable-plotting.patch
cd ..
echo "Copying BPM-Matlab sources to ${MATLAB_SRC}"
cp -r BPM-Matlab/+BPMmatlab BPM-Matlab/src ./
echo "Done"
