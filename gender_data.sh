wget http://tts.speech.cs.cmu.edu/style_models/gender_data.tar
tar -xvf gender_data.tar
rm gender_data.tar

cd gender_data

head -2000 female_only.dev.en > female_only.dev.txt
head -2000 female_only.test.en > female_only.test.txt
head -100000 female_only.train.en > female_only.train.txt

head -2000 male_only.dev.en > male_only.dev.txt
head -2000 male_only.test.en > male_only.test.txt
head -100000 male_only.train.en > male_only.train.txt

cd ..


