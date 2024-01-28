Popis webovej aplikacie: 

Jednoducha Flask Web App, ktora komunikuje s MongoDB hostovanou na cloud-based servise.
Moja Web App sluzi na pridavanie a citanie blogov. Pouzivatel sa zaregistruje a po prihlaseni uvidi na home page rozne blogy. 
Prechodom do "My Blogs" zalozky sa mu zobrazia jeho vlastne blogy, ktore moze editovat alebo mazat.
V tejto podstranke moze dalej pridavat blogy kliknutim na ikonku plus vlavo hore. 
Kazdy blog moze okomentovat a svoje komentare moze aj mazat. 
Priklad prihlasovacich udajov pouzivatela (pre testera):
email: m.bell@gmail.com, heslo: mb (nepouzivala som hashovanie, aby sa appka dala lahko testovat)

Admin ma rozhranie ciastocne modifikovane. Moze upravovat alebo odstranovat vsetky blogy. 
Taktiez dokaze odstanovat pouzivatelov. Po odstraneni pouzivatela zo systemu sa odstrania aj vsetky jeho blogy a komentare.
Admin dalej moze odstranovat lubovolne komentare a zobrazit Dashboard, kde je bar chart znazornujuci aktivitu pouzivatelov.
Priklad prihlasovacich udajov admina (pre testera):
email: j.doe@gmail.com, heslo: jd

V prilohe su aj .csv exporty databazy blog - kolekcia users a articles.


