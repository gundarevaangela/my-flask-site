import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from flask import Flask, render_template, request

app = Flask(__name__)

def create_plot(x, y, x_label, y_label, title, plot_type='bar'):
    plt.figure(figsize=(10, 6))
    
    if plot_type == 'bar':
        plt.bar(x, y, alpha=0.7)
    elif plot_type == 'line':
        plt.plot(x, y, marker='o', linestyle='-')
    
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True, linestyle='--', alpha=0.6)
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    plt.close('all')  # Явно закрываем все фигуры
    
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return plot_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            observed_values = list(map(float, request.form.get('observed_values').split(',')))
            measurements = list(map(int, request.form.get('measurements').split(',')))
            
            if len(observed_values) != len(measurements):
                return render_template('index.html', error="Количество наблюдений и измерений должно совпадать")
            
            expected_value = np.mean(observed_values)
            chi_square = sum((np.array(observed_values) - expected_value)**2 / expected_value)
            degrees_of_freedom = len(observed_values) - 1
            reduced_chi_square = chi_square / degrees_of_freedom
            
            plot1 = create_plot(
                range(1, len(observed_values)+1), 
                observed_values, 
                'Категория', 
                'Наблюдаемое значение', 
                'Наблюдаемые значения по категориям'
            )
            
            plot2 = create_plot(
                range(1, len(observed_values)+1), 
                (np.array(observed_values) - expected_value)**2 / expected_value, 
                'Категория', 
                'Вклад в χ²', 
                'Вклад каждой категории в хи-квадрат'
            )
            
            formulas = [
                {
                    'title': 'Хи-квадрат (χ²)',
                    'formula': r'\chi^2 = \sum_{i=1}^{n} \frac{(O_i - E)^2}{E}',
                    'description': 'где O_i - наблюдаемое значение, E - среднее значение'
                },
                {
                    'title': 'Степени свободы',
                    'formula': r'df = n - 1',
                    'description': 'где n - количество категорий'
                },
                {
                    'title': 'Приведенный хи-квадрат',
                    'formula': r'\text{Приведенный } \chi^2 = \frac{\chi^2}{df}',
                    'description': 'Нормировка хи-квадрата на степени свободы'
                }
            ]
            
            calculations = []
            for i in range(len(observed_values)):
                calculations.append({
                    'category': i+1,
                    'observed': observed_values[i],
                    'measurements': measurements[i],
                    'contribution': (observed_values[i] - expected_value)**2 / expected_value
                })
            
            return render_template('index.html', 
                                 chi_square=chi_square,
                                 reduced_chi_square=reduced_chi_square,
                                 degrees_of_freedom=degrees_of_freedom,
                                 expected_value=expected_value,
                                 plot1=plot1,
                                 plot2=plot2,
                                 formulas=formulas,
                                 calculations=calculations,
                                 observed_values=','.join(map(str, observed_values)),
                                 measurements=','.join(map(str, measurements)))
        
        except Exception as e:
            return render_template('index.html', error=f"Ошибка обработки данных: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)


