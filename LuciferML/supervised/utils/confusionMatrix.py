from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


def confusionMatrix(y_pred, y_val):
    """
    Takes Predicted data and Validation data as input and prepares and plots Confusion Matrix.
    """
    try:
        print('''Making Confusion Matrix [*]''')
        cm = confusion_matrix(y_val, y_pred)
        print(cm)
        ax = plt.subplot()
        sns.heatmap(cm, annot=True, fmt='g', ax=ax)
        ax.set_xlabel('Predicted labels')
        ax.set_ylabel('True labels')
        ax.set_title('Confusion Matrix')
        ax.xaxis.set_ticklabels(['0', '1'])
        ax.yaxis.set_ticklabels(['0', '1'])
        plt.show()
        print('Confusion Matrix Done [', u'\u2713', ']\n')
    except Exception as error:
        print('Building Confusion Matrix Failed with error :', error, '\n')
