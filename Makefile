# ILD分类器项目管理

.PHONY: help install test run clean lint

help:
	@echo "ILD分类器 - 可用命令:"
	@echo "  make install    - 安装依赖"
	@echo "  make test       - 运行测试"
	@echo "  make quick-test - 快速功能测试"
	@echo "  make run        - 运行示例分类"
	@echo "  make clean      - 清理输出文件"
	@echo "  make lint       - 代码检查"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --tb=short

quick-test:
	python tests/quick_test.py

run:
	python main.py -i data/input/示例数据.xlsx -o data/output/分类结果.xlsx -d data/output/详细分类.json -v

clean:
	rm -rf data/output/*
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -rf .pytest_cache
	find . -name "*.pyc" -delete

lint:
	flake8 src/ tests/ --max-line-length=100 --ignore=E501,W503
	pylint src/ --disable=C0103,R0903