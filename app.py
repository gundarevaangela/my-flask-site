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
    plt.close('all')
    
    plot_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    return plot_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            observed_values = list(map(float, request.form.get('observed_values').split(',')))
            expected_values = list(map(float, request.form.get('expected_values').split(',')))

            if len(observed_values) != len(expected_values):
                return render_template('index.html', error="Количество наблюдаемых и ожидаемых значений должно совпадать")

            chi_square_contributions = (np.array(observed_values) - np.array(expected_values))**2 / np.array(expected_values)
            chi_square = np.sum(chi_square_contributions)
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
                chi_square_contributions, 
                'Категория', 
                'Вклад в χ²', 
                'Вклад каждой категории в χ²'
            )

            calculations = []
            for i in range(len(observed_values)):
                calculations.append({
                    'category': i+1,
                    'observed': observed_values[i],
                    'expected': expected_values[i],
                    'contribution': chi_square_contributions[i]
                })

            return render_template('index.html',
                                    chi_square=chi_square,
                                    reduced_chi_square=reduced_chi_square,
                                    degrees_of_freedom=degrees_of_freedom,
                                    plot1=plot1,
                                    plot2=plot2,
                                    calculations=calculations,
                                    observed_values=','.join(map(str, observed_values)),
                                    expected_values=','.join(map(str, expected_values))
                                    )

        except Exception as e:
            return render_template('index.html', error=f"Ошибка обработки данных: {str(e)}")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)
