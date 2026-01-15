// main.js — site entry for Faith Frontier

(function () {
  "use strict";

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function initHeaderCompaction() {
    var header = document.querySelector(".site-header");
    if (!header) return;

    function syncHeader() {
      if (window.scrollY > 12) {
        header.classList.add("is-compact");
      } else {
        header.classList.remove("is-compact");
      }
    }

    syncHeader();
    window.addEventListener("scroll", syncHeader, { passive: true });
  }

  function initDailyVerse() {
    var container = document.getElementById("daily-verse");
    if (!container) return;

    function nycDateKey() {
      try {
        var fmt = new Intl.DateTimeFormat("en-US", {
          timeZone: "America/New_York",
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        });
        var parts = fmt.formatToParts(new Date());
        var y = parts.find(function (p) {
          return p.type === "year";
        }).value;
        var m = parts.find(function (p) {
          return p.type === "month";
        }).value;
        var d = parts.find(function (p) {
          return p.type === "day";
        }).value;
        return y + "-" + m + "-" + d;
      } catch (_err) {
        var dt = new Date();
        return (
          dt.getFullYear() + "-" + (dt.getMonth() + 1) + "-" + dt.getDate()
        );
      }
    }

    var key = "ff-daily-verse-" + nycDateKey();
    var cached = null;
    try {
      cached = JSON.parse(localStorage.getItem(key));
    } catch (_err) {}

    function render(v) {
      var textEl = container.querySelector(".dv-text");
      var refEl = container.querySelector(".dv-ref");
      container.style.opacity = "0";
      var ref = (v && v.reference) || "";
      var text = (v && v.text) || "";
      
      // Decode HTML entities from Bible Gateway API
      if (text) {
        var temp = document.createElement("textarea");
        temp.innerHTML = text;
        text = temp.value;
      }
      
      if (textEl) textEl.textContent = text || "Daily verse unavailable.";
      if (refEl) {
        var q = encodeURIComponent(ref);

        while (refEl.firstChild) refEl.removeChild(refEl.firstChild);
        if (ref) {
          refEl.appendChild(document.createTextNode("— " + ref + " · "));
          var versions = [
            { label: "GNV (Geneva)", version: "GNV" },
            { label: "KJV", version: "KJV" },
            { label: "AKJV", version: "AKJV" },
            { label: "NIV", version: "NIV" },
            { label: "ESV", version: "ESV" },
            { label: "NRSV", version: "NRSV" },
          ];
          versions.forEach(function (vItem, idx) {
            var a = document.createElement("a");
            a.href =
              "https://www.biblegateway.com/passage/?search=" +
              q +
              "&version=" +
              encodeURIComponent(vItem.version);
            a.target = "_blank";
            a.rel = "noopener";
            a.textContent = vItem.label;
            a.className = "verse-version-link";
            refEl.appendChild(a);
            if (idx !== versions.length - 1) {
              refEl.appendChild(document.createTextNode(" · "));
            }
          });
        }
      }
      requestAnimationFrame(function () {
        container.style.transition = "opacity 250ms ease";
        container.style.opacity = "1";
      });
    }

    if (cached) {
      render(cached);
      return;
    }

    var FALLBACK_VERSES = [
      {
        reference: "Genesis 1:1",
        text: "In the beginning God created the heaven and the earth.",
      },
      {
        reference: "Psalm 23:1",
        text: "The LORD is my shepherd; I shall not want.",
      },
      {
        reference: "Proverbs 3:5-6",
        text: "Trust in the LORD with all thine heart; and lean not unto thine own understanding. In all thy ways acknowledge him, and he shall direct thy paths.",
      },
      {
        reference: "Isaiah 40:31",
        text: "They that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles.",
      },
      {
        reference: "Jeremiah 29:11",
        text: "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end.",
      },
      {
        reference: "Matthew 5:9",
        text: "Blessed are the peacemakers: for they shall be called the children of God.",
      },
      {
        reference: "Matthew 6:33",
        text: "Seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you.",
      },
      {
        reference: "Matthew 11:28",
        text: "Come unto me, all ye that labour and are heavy laden, and I will give you rest.",
      },
      {
        reference: "John 3:16",
        text: "For God so loved the world, that he gave his only begotten Son.",
      },
      {
        reference: "John 8:12",
        text: "I am the light of the world: he that followeth me shall not walk in darkness, but shall have the light of life.",
      },
      {
        reference: "John 14:6",
        text: "I am the way, the truth, and the life: no man cometh unto the Father, but by me.",
      },
      {
        reference: "Romans 8:28",
        text: "All things work together for good to them that love God, to them who are the called according to his purpose.",
      },
      {
        reference: "Romans 12:2",
        text: "Be not conformed to this world: but be ye transformed by the renewing of your mind.",
      },
      {
        reference: "1 Corinthians 13:4-7",
        text: "Charity suffereth long, and is kind; charity envieth not; ... beareth all things, believeth all things, hopeth all things, endureth all things.",
      },
      {
        reference: "Galatians 5:22-23",
        text: "The fruit of the Spirit is love, joy, peace, longsuffering, gentleness, goodness, faith, meekness, temperance.",
      },
      {
        reference: "Ephesians 2:8-9",
        text: "By grace are ye saved through faith; and that not of yourselves: it is the gift of God.",
      },
      {
        reference: "Philippians 4:6-7",
        text: "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God.",
      },
      {
        reference: "Philippians 4:13",
        text: "I can do all things through Christ which strengtheneth me.",
      },
      {
        reference: "Colossians 3:23",
        text: "Whatsoever ye do, do it heartily, as to the Lord, and not unto men.",
      },
      {
        reference: "2 Timothy 1:7",
        text: "God hath not given us the spirit of fear; but of power, and of love, and of a sound mind.",
      },
      {
        reference: "Hebrews 11:1",
        text: "Faith is the substance of things hoped for, the evidence of things not seen.",
      },
      {
        reference: "James 1:5",
        text: "If any of you lack wisdom, let him ask of God.",
      },
      {
        reference: "1 Peter 5:7",
        text: "Casting all your care upon him; for he careth for you.",
      },
      {
        reference: "1 John 4:18",
        text: "There is no fear in love; but perfect love casteth out fear.",
      },
    ];

    function pickFallbackByDate() {
      var date = nycDateKey();
      var n = FALLBACK_VERSES.length;
      var sum = 0;
      for (var i = 0; i < date.length; i++) {
        sum = (sum * 31 + date.charCodeAt(i)) % 1000003;
      }
      var idx = sum % n;
      return FALLBACK_VERSES[idx];
    }

    var controller = null;
    var timeoutId = null;
    try {
      controller = new AbortController();
      timeoutId = setTimeout(function () {
        try {
          controller.abort();
        } catch (_err) {}
      }, 4500);
    } catch (_err) {}

    // Try multiple daily verse APIs for redundancy
    var apis = [
      {
        name: "BibleGateway",
        url: "https://www.biblegateway.com/votd/get/?format=json&version=NIV",
        parse: function (data) {
          return data && data.votd
            ? {
                text: data.votd.text || "",
                reference: data.votd.reference || "",
              }
            : null;
        },
      },
      {
        name: "OurManna",
        url: "https://beta.ourmanna.com/api/v1/get/?format=json",
        parse: function (data) {
          var item =
            data && data.verse && data.verse.details
              ? data.verse.details
              : null;
          return item
            ? { text: item.text || "", reference: item.reference || "" }
            : null;
        },
      },
    ];

    function tryAPI(apiIndex) {
      if (apiIndex >= apis.length) {
        // All APIs failed, use fallback
        if (timeoutId) clearTimeout(timeoutId);
        var v = pickFallbackByDate();
        render(v);
        try {
          localStorage.setItem(key, JSON.stringify(v));
        } catch (_err) {}
        return;
      }

      var api = apis[apiIndex];
      fetch(api.url, controller ? { signal: controller.signal } : undefined)
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          var v = api.parse(data);
          if (v && v.text && v.reference) {
            if (timeoutId) clearTimeout(timeoutId);
            render(v);
            try {
              localStorage.setItem(key, JSON.stringify(v));
            } catch (_err) {}
          } else {
            // Try next API
            tryAPI(apiIndex + 1);
          }
        })
        .catch(function () {
          // Try next API
          tryAPI(apiIndex + 1);
        });
    }

    tryAPI(0);
  }

  function boot() {
    if (window.FFNav && typeof window.FFNav.initNav === "function") {
      window.FFNav.initNav();
    }
    initHeaderCompaction();
    initDailyVerse();
  }

  ready(boot);
})();
