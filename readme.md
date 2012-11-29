Описание проекта
----------------
Проект resynthesis исследует возможность определения спектральных и временных параметров одного или нескольких акустических сигналов для осуществления синтеза — восстановления — сигналов по полученным параметрам. Иными словами, исследуется возможность синтеза звука, максимально похожего на заданный, и получения параметров отельных звуковых сигналов (компонентов), составляющих исходный звук, для дальнейшей возможности изменения этих параметров. Проект resynthesis может быть полезен композиторам и звукорежиссёрам. В теории возможность подобного синтеза звука позволила бы создавать музыкальные аранжировки на основе записей отдельных звуков существующих музыкальных инструментов без привлечения музыкантов (стоит особенно отметить, что речь идёт не о семплировании, которое имеет принципиальные ограничения, связанные с искажениями сигнала). Также в теории возможно изменение параметров музыкальных инструментов без создания соответствующего физического аналога (иными словами, моделирование музыкальных инструментов).

Цели проекта
------------
 * Исследование возможности создания описанной выше системы
 * Создание программного продукта на основе проведённых исследований
 * Определение границ применимости системы (степени приближенности синтезируемых звуков к реальным аналогам, максимально допустимой "сложности" звуков, а также наличия звуков, синтез которых указанным способом принципиально невозможен)

Задачи
------
Для достижения поставленных целей необходимо решить следующие задачи:

 * Исследование подходов к разделению звукового сигнала на составляющие части (компоненты)
 * Выбор метода синтеза звука (аддитивный синтез, частотная модуляция и т.п.) и определение существенных для него параметров
 * Определение сходства исходных и синтезируемых звуков
 * Программная реализация системы
 * Оценка (возможно субъективная) работы системы на разных классах исходных данных

Обзор существующих решений
--------------------------
Здесь будет написано про Pianotech и Kong Drum Designer.

Исследование
------------
### Подходы к решению задачи
Задачу синтеза звука, максимально соответствующего исходному, можно рассматривать как задачу оптимизации функции с определённым количеством параметров. Функцией в данном случае является мера отличия полученного звука от исходного. Параметрами функции являются параметры, используемые для синтеза. Число их может меняться и зависеть как от количества выделяемых в исходном звуке компонентов, так и от выбранного метода синтеза. В любом случае это число достаточно велико для того, чтобы можно было уверенно говорить о неприменимости классических методов оптимизации.

Рассмотрим возможность использования генетического алгоритма в качестве метода решения сформулированной задачи оптимизации.

Из существующих работ, посвящённых генетическим алгоритмам, известно, что важной частью алгоритма является целевая функция. Для некоторых сложных задач стоимость вычисления целевой функции, измеряемая количеством выполняемых процессорных инструкций, может быть крайне высокой, что приводит к неприменимости метода. Как будет показано ниже, для сформулированной изначально задачи возможно использование целевой функции на основе разницы спектральных характеристик звуков. Вычисление этих характеристик с использованием быстрого преобразование Фурье не является сложной задачей, и время решения её зависит от длительности звука. Таким образом, можно утверждать, что в смысле сложности вычисления целевой функции применение генетического алгоритм для поставленной задачи возможно.

Существующие работы в области генетических алгоритмов описывают две разновидности алгоритмов: бинарные (оперирующие битами) и непрерывные (оперирующие действительными числами). Известно, что бинарные алгоритмы применимы только для оптимизации функций с параметрами, лежащими в определённом интервале (размер интервала задаётся количеством бит, закодированных в хромосоме). Решения, получаемые такими алгоритмами, имеют фиксированную точность. Непрерывные алгоритмы лишены упомянутых ограничений. Применительно к поставленной задаче, параметрами целевой функции являются параметры, используемые в синтезе. Несмотря на то, что метод синтеза на текущем этапе считается неопределённым, можно утверждать, что непрерывный алгоритм лучше подходит для решения задачи, так как все методы синтеза оперируют такими величинами как длительность и частота, которые по своей природе являются действительными числами.

Здесь будет написано про мутацию и скрещивание.
### Выбор целевой функции
Здесь будет рассказано про выбор целевой функции.
### Выбор метода синтеза
Здесь будет рассказано про выбор метода синтеза.
