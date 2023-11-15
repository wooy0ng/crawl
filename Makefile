search:
	python main.py --config config/$(domain).yaml --task search

updatedb:
	python main.py --config config/$(domain).yaml --task update

labeling:
	python main.py --task update --do_labeling True