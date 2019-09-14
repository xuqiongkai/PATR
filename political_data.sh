wget http://tts.speech.cs.cmu.edu/style_models/political_data.tar
tar -xvf political_data.tar
rm political_data.tar


cd political_data
head -2000 democratic_only.dev.en > democratic_only.dev.txt 
head -2000 democratic_only.test.en > democratic_only.test.txt
head -100000 democratic_only.train.en > democratic_only.train.txt

head -2000 republican_only.dev.en > republican_only.dev.txt
head -2000 republican_only.test.en > republican_only.test.txt
head -100000 republican_only.train.en > republican_only.train.txt

cd ..

