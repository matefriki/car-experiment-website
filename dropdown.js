window.addEventListener('load', () => {
    let dropdowns = document.body.querySelectorAll(".dropdown-component");
    dropdowns.forEach(Dropdown.setup);
});

let Dropdown = {
    setup: (base) => {
        let optList = base.dataset.options.split(",").map((label) => label.trim());
        Dropdown.createElements(base, optList);
        Dropdown.style(base, base.clientWidth, base.clientHeight);
        window.addEventListener("click", () => Dropdown.setVisibility(base, false));
        let observer = new ResizeObserver(Dropdown.resize);
        observer.observe(base);
    },

    createElements: (base, optList) => {
        let value = document.createElement("div");
        let button = document.createElement("div");
        let options = document.createElement("div");

        base.classList.add("drop-base");
        value.classList.add("drop-value");
        button.classList.add("drop-button");
        options.classList.add("drop-options");

        button.addEventListener("click", (e) => {
            Dropdown.setVisibility(base, options.style.display == "none")
            e.stopPropagation();
        });

        options.style.display = "none";

        let optElems = [];
        optList.forEach((label) => {
            let curr = document.createElement("div");
            curr.classList.add("drop-option");
            curr.innerHTML = label;
            curr.addEventListener("click", 
                Dropdown.select.bind(null, curr, base, value));
            optElems.push(curr);
            options.appendChild(curr);
        });

        base.appendChild(value);
        base.appendChild(button);
        base.appendChild(options);

        Dropdown.setValue(base, optList[0]);
        button.innerHTML = "&#9660;";
    },

    resize: (entries) => {
        entries.forEach((entry) => {
            Dropdown.style(entry.target, entry.contentRect.width, entry.contentRect.height);
        });
    },

    style: (base, width, height) => {
        let value = base.querySelector(".drop-value");
        let button = base.querySelector(".drop-button");
        let options = base.querySelector(".drop-options");
        let optList = base.querySelectorAll(".drop-option");

        let padding = height * .2;
        Dropdown.applyStyle(base, [
            ["borderBottom", `${height * .16}px solid ${Dropdown.shadowColor}`]
        ]);

        Dropdown.applyStyle(value, [
            ["paddingLeft", (padding) + "px"],
            ["lineHeight", height + "px"],
            ["fontSize", (height * .4) + "px"]
        ]);

        Dropdown.applyStyle(button, [
            ["fontSize", (height * .35) + "px"],
            ["lineHeight", height + "px"]
        ]);

        Dropdown.applyStyle(options, [
            ["top", height + "px"],
            ["fontSize", (height * .35) + "px"],
            ["width", width - (padding * 2)]
        ]);

        optList.forEach((opt, ind) => {
            Dropdown.applyStyle(opt, [
                ["padding", `${padding * .5}px ${padding}px`],
            ])
            if(ind == 0) opt.style.paddingTop = padding + "px";
            else if(ind == optList.length - 1) opt.style.paddingBottom = padding + "px";;
        });
    },

    applyStyle: (elem, styling) => {
        styling.forEach((prop) => {
            elem.style[prop[0]] = prop[1];
        });
    },

    select: (opt, base, value) => {
        Dropdown.setValue(base, opt.innerHTML);
        Dropdown.setVisibility(base, false);
        console.log(this);
    },

    setValue: (base, opt) => {
        let value = base.querySelector(".drop-value");
        base.dataset.value = opt;
        value.innerHTML = opt;
    },

    setVisibility: (base, visible) => {
        let options = base.querySelector(".drop-options");
        options.style.display = visible ? "block" : "none";
    },

    shadowColor: "#2a79ad"
}