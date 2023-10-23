import matplotlib.pyplot as plt
import pandas as pd
import requests
import json


class DrawGraph:

    """ Класс графиков """

    def __init__(self, id_number, name, gt_corners, rb_corners, mean, mean_max, mean_min,
                 floor_mean, floor_max, floor_min, ceiling_mean, ceiling_max, ceiling_min):

        self.id_number = id_number
        self.name = name
        self.gt_corners = gt_corners
        self.rb_corners = rb_corners
        self.mean = mean
        self.mean_max = mean_max
        self.mean_min = mean_min
        self.floor_mean = floor_mean
        self.floor_max = floor_max
        self.floor_min = floor_min
        self.ceiling_mean = ceiling_mean
        self.ceiling_max = ceiling_max
        self.ceiling_min = ceiling_min

    def create_plots(self, size='line'):

        """ Метод отрисовки графиков """

        def colors(args):

            """ Функция выбора цвета """

            green = (89/255, 225/255, 96/255)
            red = (239/255, 71/255, 37/255)
            blue = (67/255, 176/255, 226/255)

            color = [green, red, blue]

            if len(args) == 2:

                if args[0] == args[1]: return [color[2], color[0]]                  # зеленый - GT == RB
                return [color[2], color[1]]                                         # красный - GT != RB

            if args[1] < args[2] < args[0]: return [color[2], color[2], color[0]]   # зеленый - в диапазоне max/min
            return [color[2], color[2], color[1]]                                   # красный - не в диапазоне max/min

        # стиль графика

        if size == 'colum':                                                         # графики колонками

            fig, axes = plt.subplots(4, 1, figsize=(10, 5))
            plt.subplots_adjust(hspace=1.5)
            fig_text_id = [0.021, 0.95]
            fig_text_name = [0.02, 0.915]

        else:                                                                       # графики в линию

            fig, axes = plt.subplots(1, 4, figsize=(14, 1))
            plt.subplots_adjust(hspace=35.5)
            plt.subplots_adjust(wspace=0.4, top=0.7, bottom=0.3)
            fig_text_id = [0.021, 0.55]
            fig_text_name = [0.02, 0.35]

        # графики

        corners = [self.rb_corners, self.gt_corners]
        axes[0].barh(['rb', 'gt'], corners, color=colors(corners))

        mean = [self.mean_max, self.mean_min, self.mean]
        axes[1].barh(['max', 'min', 'mean'], mean, color=colors(mean))

        floor = [self.floor_max, self.floor_min, self.floor_mean]
        axes[2].barh(['max', 'min', 'floor'], floor, color=colors(floor))

        ceiling = [self.ceiling_max, self.ceiling_min, self.ceiling_mean]
        axes[3].barh(['max', 'min', 'ceiling'], ceiling, color=colors(ceiling))

        # заголовки

        col = ['red', 'black']

        gt_rb = self.gt_corners == self.rb_corners
        axes[0].set_title(f'GT {["!=", "=="][gt_rb]} RB', color=col[gt_rb], fontsize=10)

        min_m, max_m = self.mean_min < self.mean, self.mean < self.mean_max
        axes[1].set_title(f'min {[">", "<"][min_m]} Mean {[">", "<"][max_m]} max', color=col[min_m and max_m], fontsize=10)

        min_f, max_f = self.floor_min < self.floor_mean, self.floor_mean < self.floor_max
        axes[2].set_title(f'min {[">", "<"][min_f]} Floor {[">", "<"][max_f]} max', color=col[min_f and max_f], fontsize=10)

        min_c, max_c = self.ceiling_min < self.ceiling_mean, self.ceiling_mean < self.ceiling_max
        axes[3].set_title(f'min {[">", "<"][min_c]} Ceiling {[">", "<"][max_c]} max', color=col[min_c and max_c], fontsize=10)

        # общий заголовок

        fig.text(fig_text_id[0], fig_text_id[1], f'ID# {self.id_number}', fontsize=10)
        fig.text(fig_text_name[0], fig_text_name[1], f'{self.name[:14]}', fontsize=10)

        plt.savefig(f'plots/{self.id_number}')


def draw_plots(url_link, need_id, max_iteration=0, size='line'):

    """ Создаем графики """

    response = requests.get(url_link)

    with open("json/deviation.json", "wb") as file: file.write(response.content)
    with open('json/deviation.json') as json_file: data = json.load(json_file)

    attribute = ['id_number', 'name', 'gt_corners', 'rb_corners', 'mean', 'max', 'min',
                 'floor_mean', 'floor_max', 'floor_min', 'ceiling_mean', 'ceiling_max', 'ceiling_min']

    pandas_data = {attr: [] for attr in attribute}

    for id_number in data['name']:

        if max_iteration != 0 and int(id_number) == max_iteration: break
        if need_id: id_number = str(need_id)

        for attr in attribute: pandas_data[attr].append(id_number if attr == 'id_number' else data[attr][id_number])

        grap = DrawGraph(*(id_number if attr == 'id_number' else data[attr][id_number] for attr in attribute))
        grap.create_plots(size)

        if need_id: break

    df = pd.DataFrame(pandas_data)
    df.to_csv('table.csv',  index=False)

    return pandas_data


# url = "https://ai-process-sandy.s3.eu-west-1.amazonaws.com/purge/deviation.json"
# параметры - draw_plots([url адрес], [показать конкретный id], [max_iteration=int], [size='line'/'colum'])
# draw_plots(url, False, max_iteration=5)
