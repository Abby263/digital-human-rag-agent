.PHONY: start stop restart clean

start:
	@echo "Starting the Digital Human Agent..."
	@poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

stop:
	@echo "Stopping the Digital Human Agent..."
	@# Command to stop the server will be added here

restart:
	@echo "Restarting the Digital Human Agent..."
	@make stop
	@make start

clean:
	@echo "Cleaning up generated files..."
	@rm -f ./static/generated_video.mp4
	@rm -f ./static/source_image.png
	@rm -f ./static/audio.wav
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete 