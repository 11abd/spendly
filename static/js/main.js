// main.js — students will add JavaScript here as features are built

document.addEventListener('DOMContentLoaded', function () {
    var trigger = document.getElementById('how-it-works-btn');
    var modal = document.getElementById('video-modal');
    var closeBtn = document.getElementById('modal-close-btn');
    var iframe = document.getElementById('modal-video-iframe');
    var videoUrl = 'https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1';

    if (!trigger || !modal || !closeBtn || !iframe) return;

    function openModal(event) {
        event.preventDefault();
        iframe.src = videoUrl;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('active');
        iframe.src = ''; // stops playback — reloading the src would restart it
        document.body.style.overflow = '';
    }

    trigger.addEventListener('click', openModal);
    closeBtn.addEventListener('click', closeModal);

    modal.addEventListener('click', function (event) {
        if (event.target === modal) closeModal();
    });

    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && modal.classList.contains('active')) closeModal();
    });
});
