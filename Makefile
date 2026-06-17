VENV_DIR = venv
VENV_BIN = $(VENV_DIR)/bin
PYTHON = $(VENV_BIN)/python3
PIP = $(VENV_BIN)/pip
MAIN = src/main.py
#FILE = src/maps/easy/01_linear_path.txt
#FILE = src/maps/easy/02_simple_fork.txt
#FILE = src/maps/easy/03_basic_capacity.txt
#FILE = src/maps/medium/01_dead_end_trap.txt
#FILE = src/maps/medium/02_circular_loop.txt
#FILE = src/maps/medium/03_priority_puzzle.txt
#FILE = src/maps/hard/01_maze_nightmare.txt
#FILE = src/maps/hard/02_capacity_hell.txt
#FILE = src/maps/hard/03_ultimate_challenge.txt
#FILE = src/maps/challenger/01_the_impossible_dream.txt
#FILE = src/maps/challenger/02_without_color.txt
FILE = src/maps/challenger/03_tester_aval.txt

REQS = requirements.txt

all: install

$(VENV_BIN)/activate:
	@echo "Creating virtual environment"
	python3 -m venv $(VENV_DIR)

install: $(VENV_BIN)/activate
	@echo "Installing dependencies from $(REQS)"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r $(REQS)
	@echo "everything installed"

run: $(VENV_BIN)/activate
	$(PYTHON) $(MAIN) $(FILE)

visual: $(VENV_BIN)/activate
	$(PYTHON) $(MAIN) $(FILE) --visual

debug: $(VENV_BIN)/activate
	$(PYTHON) -m pdb $(MAIN) $(FILE)

lint: $(VENV_BIN)/activate
	$(VENV_BIN)/flake8 . --exclude=$(VENV_DIR),__pycache__,.mypy_cache
	$(VENV_BIN)/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache

fclean: clean
	rm -fr $(VENV_DIR)

.PHONY: all install run visual debug lint clean fclean