
function convertToChartDateFormat(dateTimeString) {
    const date = new Date(dateTimeString);
    return { year: date.getFullYear(), month: date.getMonth() + 1, day: date.getDate() };
};

export default convertToChartDateFormat;