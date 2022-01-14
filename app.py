import streamlit as st
import ETL
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout='wide')

@st.cache(allow_output_mutation=True)
def load_data():
    daily_info = ETL.load_daily_info()
    dist_distr_info = ETL.load_district_distr_info()
    daily_district_data = ETL.load_daily_district_data()
    return daily_info, dist_distr_info, daily_district_data

daily_info, dist_distr_info, daily_district_data = load_data()

st.header('''
Кол-во ежедневных активаций кода и регистраций.
''')

with st.expander('Показать'):

    st.plotly_chart(daily_info[1], use_container_width=True)
    st.write(f'''
    * Кол-во ежедневной активации кодов и регистраций за месяц увеличилось в 10 раз
    * Кол-во активаций кода каждый день (кроме одного) выше кол-ва регистраций
    * Так как регистрация происходит во время активации это означает, что некоторые пользователи активировавшие код уже были зарегистрированны (их число на диаграмме показанно в столбцах)
    * Кол-во уже зарегестрированных пользователей, активирующих код, растет
    * На графике можно увидеть ярковыраженные пики
    * Пики со временем выражены все ярче и ярче
    * Среднее время между пиками: {round(daily_info[2], 2)} дней
    * Погрешность (среднеквадратическое отклонение): {round(daily_info[3], 2)} дней
    * Вполне вероятно, срок службы продукта примерно 3-4 дня, и покупатель возвращается за ним в магазин именно через этот промежуток времени
    ''')


st.header('''Региональная структура дистрибуции продукта.''')
with st.expander('Показать'):
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(dist_distr_info[3], use_container_width=True)
    with col2:
        st.plotly_chart(dist_distr_info[1], use_container_width=True)

    st.write('''
    * По кол-ву активированных кодов:
      - Первое место занимает Центральный Округ
      - Второе- Приволжский
      - Третье- Северо-Западный
    * Чем ближе к центральной части России, тем больше активированных кодов
    * Отсюда можно сделать вывод, что производство может располагаться в центральной части России или же даже в зарубежных западных странах
    * Наибольшее число активаций, а следовательно и продаж, в регионах с наибольшей покупательной способностью населения
    ''')

    st.plotly_chart(dist_distr_info[4], use_container_width=True)

    st.write('''
    * После пересчета кол-ва активаций на душу населения доли Уральского и Северо-Западного округов значительно увеличились
    ''')

st.header('''
Кол-во ежедневных активаций кода по регионам.
''')

with st.expander('Показать'):
    with st.form('district choice'):
        districts = st.multiselect(label='Выберите Округ', options=daily_district_data.FederalDistrict_Name.unique(), default=daily_district_data.FederalDistrict_Name.unique())
        st.form_submit_button(label='Выбрать')

    fig = px.line(daily_district_data[daily_district_data.FederalDistrict_Name.isin(districts)],
                  x='Date',
                  y='Event_Count',
                  color='FederalDistrict_Name',
                  color_discrete_sequence=px.colors.qualitative.Safe,
                  labels={
                      "Event_Count": "Кол-во активаций/регистраций",
                      "Date": "Дата",
                      "FederalDistrict_Name": "Название федерального округа"
                  })
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

    st.write('''
    * Ежедневная активация кодов изменялась в разных округах примерно одиинаково
    ''')


