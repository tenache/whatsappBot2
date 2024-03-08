try {
    // Try using a numeric separator
    eval('1_000');
    console.log('Numeric separator is supported!');
} catch (e) {
    console.log('Numeric separator is not supported.');
}
