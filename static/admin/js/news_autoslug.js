
(function() {
  'use strict';

  // Transliteration map — Hindi chars to Roman
  const hi2en = {
    'अ':'a','आ':'aa','इ':'i','ई':'ee','उ':'u','ऊ':'oo','ए':'e','ऐ':'ai','ओ':'o','औ':'au',
    'क':'k','ख':'kh','ग':'g','घ':'gh','च':'ch','छ':'chh','ज':'j','झ':'jh',
    'ट':'t','ठ':'th','ड':'d','ढ':'dh','त':'t','थ':'th','द':'d','ध':'dh','न':'n',
    'प':'p','फ':'ph','ब':'b','भ':'bh','म':'m','य':'y','र':'r','ल':'l','व':'v',
    'श':'sh','ष':'sh','स':'s','ह':'h','ं':'n','ः':'h','ा':'a','ि':'i','ी':'ee',
    'ु':'u','ू':'oo','े':'e','ै':'ai','ो':'o','ौ':'au','्':'','ृ':'ri',
    'ञ':'ny','ण':'n','ङ':'n','झ':'jh','क्ष':'ksh','त्र':'tr','ज्ञ':'gn',
  };

  function hindiToSlug(text) {
    if (!text) return '';
    let result = '';
    for (let i = 0; i < text.length; i++) {
      const ch = text[i];
      if (hi2en[ch] !== undefined) {
        result += hi2en[ch];
      } else if (/[a-zA-Z0-9]/.test(ch)) {
        result += ch.toLowerCase();
      } else if (/[\s\-_।,.]/.test(ch)) {
        result += '-';
      }
      // skip other chars
    }
    // clean up slug
    return result
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '')
      .slice(0, 80);
  }

  function updateSlugFromHindi() {
    const titleHi = document.getElementById('id_title_hi');
    const slugField = document.getElementById('id_slug');
    const titleEn = document.getElementById('id_title_en');
    if (!titleHi || !slugField) return;

    // Only auto-fill if slug is empty (new article)
    if (slugField.dataset.userEdited === 'true') return;

    const hiSlug = hindiToSlug(titleHi.value);
    const enSlug = (titleEn && titleEn.value)
      ? titleEn.value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 80)
      : '';

    slugField.value = enSlug || hiSlug || '';
  }

  function autoSummary() {
    // Auto-fill summary from content if summary is empty
    const contentHi = document.getElementById('id_content_hi');
    const summaryHi = document.getElementById('id_summary_hi');
    if (!contentHi || !summaryHi) return;
    if (summaryHi.value.trim()) return; // already filled
    const words = contentHi.value.trim().split(/\s+/).slice(0, 30).join(' ');
    if (words.length > 10) summaryHi.value = words + '...';
  }

  document.addEventListener('DOMContentLoaded', function () {
    const titleHi  = document.getElementById('id_title_hi');
    const titleEn  = document.getElementById('id_title_en');
    const slugField = document.getElementById('id_slug');
    const contentHi = document.getElementById('id_content_hi');
    const summaryHi = document.getElementById('id_summary_hi');

    if (!titleHi) return;

    // Mark if user manually edits slug
    if (slugField) {
      slugField.addEventListener('input', function () {
        slugField.dataset.userEdited = 'true';
      });
      // If slug is empty, it's a new article — enable auto
      if (!slugField.value.trim()) {
        slugField.dataset.userEdited = 'false';
      }
    }

    // Auto-slug on typing title
    titleHi.addEventListener('input', updateSlugFromHindi);
    if (titleEn) titleEn.addEventListener('input', updateSlugFromHindi);

    // Auto-summary when leaving content field
    if (contentHi) {
      contentHi.addEventListener('blur', autoSummary);
    }

    // Style the tag widget for better UX
    const tagSelect = document.getElementById('id_tags_from');
    const tagSelectTo = document.getElementById('id_tags_to');
    if (tagSelect) {
      // Add helper text above tags
      const helper = document.createElement('div');
      helper.style.cssText = 'font-size:12px;color:#888;margin-bottom:6px;padding:6px 10px;background:#f8f9fa;border-radius:4px;border-left:3px solid #e60026';
      helper.innerHTML = '💡 <strong>Tip:</strong> Select tags from the left list and click "→" to add them. To create a new tag, go to <a href="/admin/news/tag/add/" target="_blank" style="color:#e60026">Admin → Tags → Add Tag</a> first.';
      if (tagSelect.closest('.selector')) {
        tagSelect.closest('.selector').insertAdjacentElement('beforebegin', helper);
      }
    }

    // Add "New Tag" quick-add button next to tags
    if (tagSelectTo) {
      const addTagBtn = document.createElement('a');
      addTagBtn.href = '/admin/news/tag/add/?_popup=1';
      addTagBtn.className = 'related-widget-wrapper-link add-related';
      addTagBtn.title = 'Add a new Tag';
      addTagBtn.style.cssText = 'margin-left:8px;color:#e60026;font-weight:600;font-size:12px;text-decoration:none;display:inline-block;padding:4px 10px;border:1px solid #e60026;border-radius:4px';
      addTagBtn.innerHTML = '+ New Tag';
      addTagBtn.onclick = function(e) {
        e.preventDefault();
        window.open(this.href, 'add_tag', 'height=500,width=800,resizable=yes,scrollbars=yes');
      };
      if (tagSelectTo.parentNode) {
        tagSelectTo.parentNode.appendChild(addTagBtn);
      }
    }
  });
})();
