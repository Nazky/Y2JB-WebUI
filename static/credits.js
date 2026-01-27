document.addEventListener('DOMContentLoaded', () => {
    const credits = [
        {
            author: "Gezine",
            project: "Y2JB",
            role: "Core Project",
            url: "https://github.com/Gezine/Y2JB/",
            authorUrl: "https://github.com/Gezine",
            avatar: "https://avatars.githubusercontent.com/u/30000519?v=4"
        },
        {
            author: "rmuxnet",
            project: "Y2JB-WebUI",
            role: "Contributor",
            url: "https://github.com/Nazky/Y2JB-WebUI",
            authorUrl: "https://github.com/rmuxnet",
            avatar: "https://avatars.githubusercontent.com/u/116457149?v=4"
        },
        {
            author: "itsPLK",
            project: "ps5_y2jb_autoloader",
            role: "Inspiration",
            url: "https://github.com/itsPLK/ps5_y2jb_autoloader",
            authorUrl: "https://github.com/itsPLK",
            avatar: "https://avatars.githubusercontent.com/u/209955039?s=200&v=4"
        },
        {
            author: "EchoStretch",
            project: "kstuff",
            role: "Payload",
            url: "https://github.com/EchoStretch/kstuff",
            authorUrl: "https://github.com/EchoStretch",
            avatar: "https://avatars.githubusercontent.com/u/98502641?v=4"
        },
        {
            author: "voidwhisper-ps",
            project: "ShadowMount",
            role: "Payload",
            url: "https://github.com/adel-ailane/ShadowMount",
            authorUrl: "https://github.com/voidwhisper-ps",
            avatar: "https://avatars.githubusercontent.com/u/253620578?v=4"
        },
        {
            author: "drakmor",
            project: "ftpsrv",
            role: "Payload",
            url: "https://github.com/drakmor/ftpsrv",
            authorUrl: "https://github.com/drakmor",
            avatar: "https://avatars.githubusercontent.com/u/1344732?v=4"
        },
        {
            author: "john-tornblom",
            project: "websrv-ps5",
            role: "Payload",
            url: "https://github.com/ps5-payload-dev/websrv",
            authorUrl: "https://github.com/john-tornblom",
            avatar: "https://avatars.githubusercontent.com/u/547534?v=4"
        }
    ];

    const container = document.getElementById('credits-grid');
    
    credits.forEach((credit, index) => {
        const card = document.createElement('div');
        card.style.animationDelay = `${index * 100}ms`;
        card.className = `surface border rounded-xl p-5 hover:border-brand-blue/50 transition-all duration-300 group animate-slide-up opacity-0 fill-mode-forwards`;

        card.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex items-center gap-3">
                    <img src="${credit.avatar}" alt="${credit.author}" class="w-10 h-10 rounded-full object-cover shadow-lg border border-white/10 bg-surface">
                    <div>
                        <h3 class="font-bold text-lg leading-tight group-hover:text-brand-light transition-colors">
                            ${credit.author}
                        </h3>
                        <span class="text-[10px] opacity-50 uppercase tracking-wider font-bold border border-white/10 px-1.5 py-0.5 rounded">
                            ${credit.role}
                        </span>
                    </div>
                </div>
                <a href="${credit.authorUrl}" target="_blank" class="opacity-40 hover:opacity-100 hover:text-brand-light transition-all">
                    <i class="fa-brands fa-github text-xl"></i>
                </a>
            </div>
            
            <div class="mt-4 pt-4 border-t border-oled-border">
                <div class="flex items-center justify-between text-sm">
                    <span class="opacity-70 font-mono text-xs">${credit.project}</span>
                    <a href="${credit.url}" target="_blank" class="flex items-center gap-2 text-xs font-bold text-brand-light opacity-80 hover:opacity-100 transition-opacity">
                        <span>View Project</span>
                        <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                    </a>
                </div>
            </div>
        `;
        
        container.appendChild(card);
    });
});
