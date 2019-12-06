const galleryContainer = document.querySelector('.gallery-horizontal-container');
const gallery = document.querySelector('.gallery-horizontal');
const numTiles = gallery.children.length;
const scrollNext = document.querySelector('.scroll-button.next');
const scrollPrevious = document.querySelector('.scroll-button.previous');
const scrollTolerance = 50;

function showScrollButtons() {
  const galleryWidth = gallery.scrollWidth;
  if (numTiles > 1 && galleryWidth > gallery.clientWidth) {
    const scrollPosition = gallery.scrollLeft;
    if (scrollPosition > scrollTolerance) {
      scrollPrevious.style.display = 'inline-block';
    } else {
      scrollPrevious.style.display = 'none';
    }
    if (scrollPosition + gallery.clientWidth < galleryWidth - scrollTolerance) {
      scrollNext.style.display = 'inline-block';
    } else {
      scrollNext.style.display = 'none';
    }
  } else {
    scrollNext.style.display = 'none';
    scrollPrevious.style.display = 'none';
  }
}

function scrollGallery(direction) {
  const averageItemWidth = gallery.scrollWidth / numTiles;
  gallery.scrollBy(averageItemWidth * direction, 0);
}

(function () {
  scrollNext.addEventListener('click', function () { scrollGallery(1) });
  scrollPrevious.addEventListener('click', function () { scrollGallery(-1) });

  gallery.addEventListener('scroll', showScrollButtons);

  window.addEventListener('resize', showScrollButtons);
  window.addEventListener('load', showScrollButtons);
})();