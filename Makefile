WORKDIR = yatube

style:
	black -S -l 79 $(WORKDIR)
	isort $(WORKDIR)
	flake8 $(WORKDIR)
	mypy $(WORKDIR)
	djhtml -i -t 2 $(WORKDIR) 
	