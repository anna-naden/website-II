conda activate website-II
cd /home/anna_user2/projects/website/py
python make_pickle.py > /home/anna_user2/projects/website-II/sh/daily-out.txt
python make_county_features.py  >> /home/anna_user2/projects/website-II/sh/daily-out.txt
python batch_write_county_features.py >> /home/anna_user2/projects/website-II/sh/daily-out.txt
python make_states_features.py >> /home/anna_user2/projects/website-II/sh/daily-out.txt
