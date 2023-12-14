'use strict';

const leftBtn = document.querySelector('.left');
const rightBtn = document.querySelector('.right');

const carouselItems = Array.from(document.querySelectorAll('.carousel-item'));
const navItems = Array.from(document.querySelectorAll('.nav-item-carousel'));
const CAROUSEL_SIZE = carouselItems.length;

leftBtn.addEventListener('click', swipe);
rightBtn.addEventListener('click', swipe);

function swipe(e){
    const currentCarouselItem = document.querySelector('.carousel-item.active');
    const currentIndex = carouselItems.indexOf(currentCarouselItem);

    let nextIndex;

    if(e.currentTarget.classList.contains('left')){
        if(currentIndex === 0){
            nextIndex = CAROUSEL_SIZE - 1;
        }
        else{
            nextIndex = currentIndex - 1;
        }
    }
    else{
        if(currentIndex === CAROUSEL_SIZE - 1){
            nextIndex = 0;
        }
        else{
            nextIndex = currentIndex + 1;
        }
    }

    carouselItems[nextIndex].classList.add('active');
    navItems[nextIndex].classList.add('active');
    currentCarouselItem.classList.remove('active');
    navItems[currentIndex].classList.remove('active');
}

const dotItems = Array.from(document.querySelectorAll('.nav-item-carousel'));

const dotOne = document.querySelector('.dot-1');
const dotTwo = document.querySelector('.dot-2');
const dotThree = document.querySelector('.dot-3');
const dotFour = document.querySelector('.dot-4');

dotOne.addEventListener('click', dotNavigation);
dotTwo.addEventListener('click', dotNavigation);
dotThree.addEventListener('click', dotNavigation);
dotFour.addEventListener('click', dotNavigation);

function dotNavigation(e){
    const currentDotItem = document.querySelector('.nav-item-carousel.active');
    const currentCarouselItem = document.querySelector('.carousel-item.active');
    const currentIndex = dotItems.indexOf(currentDotItem);

    let newIndex;

    if(e.currentTarget.classList.contains('dot-1')){
        newIndex = 0;
    }
    else if(e.currentTarget.classList.contains('dot-2')){
        newIndex = 1;
    }
    else if(e.currentTarget.classList.contains('dot-3')){
        newIndex = 2;
    }
    else if(e.currentTarget.classList.contains('dot-4')){
        newIndex = 3;
    }

    
    if(currentDotItem != dotItems[newIndex]) {
        carouselItems[newIndex].classList.add('active');
        navItems[newIndex].classList.add('active');
        currentDotItem.classList.remove('active');
        currentCarouselItem.classList.remove('active');
        navItems[currentIndex].classList.remove('active');
    }
}