let Bullet = {
    setup: (base) => {
        let labels = base.querySelectorAll(".label");
        let boxes = base.querySelectorAll(".box");

        boxes.forEach((box) => {
            box.addEventListener("click", () => {
                if(Bullet.isDisabled(base)) return;
                let count = Bullet.countSelections(base);
                let label = box.parentElement.querySelector(".label");
                if(box.classList.contains("selected")) {
                    if(count > 1) {
                        box.classList.remove("selected");
                        if(label.classList.contains("selected")) {
                            Bullet.shiftMain(base);
                        }
                    }
                } else {
                    box.classList.add("selected");
                }

                Bullet.updateTag(base);
            });
        });

        labels.forEach((label) => {
            label.addEventListener("click", () => {
                if(Bullet.isDisabled(base)) return;
                let box = label.parentElement.querySelector(".box");
                Bullet.clearMain(base);
                label.classList.add("selected");
                box.classList.add("selected");
                Bullet.updateTag(base);
            });
        });

        Bullet.updateTag(base);
    },

    clearMain: (base) => {
        base.querySelectorAll(".label").forEach((label) => label.classList.remove("selected"));
    },

    shiftMain: (base) => {
        let boxes = base.querySelectorAll(".box");
        
        Bullet.clearMain(base);
        Array.from(boxes).every((box) => {
            if(box.classList.contains("selected")) {
                let label = box.parentElement.querySelector(".label");
                label.classList.add("selected");
                return false;
            }
            return true;
        });
    },

    countSelections: (base) => {
        return base.querySelectorAll(".box.selected").length;
    },

    toString: (base) => {
        let boxes = base.querySelectorAll(".box");

        let selection = [];
        boxes.forEach((box) => {
            if(box.classList.contains("selected")) {
                let label = box.parentElement.querySelector(".label");
                if(label.classList.contains("selected")) {
                    selection.unshift(label.innerText);
                } else {
                    selection.push(label.innerText);
                }
            }
        });

        return selection.map((strat) => strat.replace(/ /g, '_')).join(',').toLowerCase();
    },

    updateTag: (base) => {
        let str = Bullet.toString(base);
        base.dataset.value = str;
    },

    isDisabled: (base) => {
        return base.classList.contains("disabled");
    }
}