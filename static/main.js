document.addEventListener('DOMContentLoaded', () => {
    const generationForm = document.getElementById('generation-form');
    const generateBtn = document.getElementById('generate-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');
    const progressMessage = document.getElementById('progress-message');
    const resultContainer = document.getElementById('result-container');
    const resultVideo = document.getElementById('result-video');
    const downloadLink = document.getElementById('download-link');
    const generationTime = document.getElementById('generation-time');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    const resetBtnSuccess = document.getElementById('reset-btn-success');
    const resetBtnError = document.getElementById('reset-btn-error');
    const loadingOverlay = document.getElementById('loading-overlay');

    const stages = {
        prompt: document.getElementById('stage-prompt'),
        image: document.getElementById('stage-image'),
        audio: document.getElementById('stage-audio'),
        video: document.getElementById('stage-video'),
    };

    let evtSource;

    function resetUI() {
        generationForm.reset();
        generateBtn.disabled = false;
        progressContainer.classList.add('hidden');
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        loadingOverlay.classList.add('hidden');
        generationForm.classList.remove('hidden');

        progressBar.style.width = '0%';
        progressPercentage.textContent = '0%';
        progressMessage.textContent = '';

        Object.values(stages).forEach(stage => {
            stage.classList.remove('in_progress', 'complete');
        });
    }

    generationForm.addEventListener('submit', (event) => {
        event.preventDefault();
        
        const formData = new FormData(generationForm);
        const characterstics = formData.get('characterstics');
        const script = formData.get('script');

        generateBtn.disabled = true;
        generationForm.classList.add('hidden');
        resultContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        progressContainer.classList.remove('hidden');
        loadingOverlay.classList.remove('hidden');

        const queryParams = new URLSearchParams({ characterstics, script });
        evtSource = new EventSource(`/generate?${queryParams}`);

        evtSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Update progress bar
            progressBar.style.width = `${data.progress}%`;
            progressPercentage.textContent = `${data.progress}%`;
            progressMessage.textContent = data.message;
            
            // Update stage status
            if (stages[data.stage]) {
                Object.values(stages).forEach(s => s.classList.remove('in_progress'));
                stages[data.stage].classList.add(data.status);
                // Mark previous stages as complete
                const stageNames = Object.keys(stages);
                const currentStageIndex = stageNames.indexOf(data.stage);
                for (let i = 0; i < currentStageIndex; i++) {
                    stages[stageNames[i]].classList.remove('in_progress');
                    stages[stageNames[i]].classList.add('complete');
                }
            }

            if (data.status === 'complete' && data.stage === 'video') {
                resultVideo.src = data.message;
                downloadLink.href = data.message;
                resultContainer.classList.remove('hidden');
                progressContainer.classList.add('hidden');
                loadingOverlay.classList.add('hidden');
                evtSource.close();

                if (data.total_time) {
                    const minutes = Math.floor(data.total_time / 60);
                    const seconds = Math.floor(data.total_time % 60);
                    generationTime.textContent = `Total generation time: ${minutes}m ${seconds}s`;
                    generationTime.classList.remove('hidden');
                }
            }

            if (data.status === 'error') {
                errorMessage.textContent = data.message;
                errorContainer.classList.remove('hidden');
                progressContainer.classList.add('hidden');
                loadingOverlay.classList.add('hidden');
                generateBtn.disabled = false;
                evtSource.close();
            }
        };

        evtSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            errorMessage.textContent = 'Connection to the server failed. Please check your network or restart the server.';
            errorContainer.classList.remove('hidden');
            progressContainer.classList.add('hidden');
            loadingOverlay.classList.add('hidden');
            generateBtn.disabled = false;
            evtSource.close();
        };
    });

    resetBtnSuccess.addEventListener('click', () => {
        resetUI();
    });

    resetBtnError.addEventListener('click', () => {
        resetUI();
    });
}); 