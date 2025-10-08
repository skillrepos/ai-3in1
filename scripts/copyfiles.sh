mkdir data
mkdir deployment
cp ../data/offices.* data/
cp ../deployment/* deployment/
cp ../*classification.py .
cp ../requirements.txt .
cp ../streamlit_app.py .
mv deployment/Dockerfile .
mv deployment/README.md .

