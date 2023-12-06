import Fingerprint2 from 'fingerprintjs2';

require('./fingerprint2')

function x64hash128(s, seed) {
    return Fingerprint2.x64hash128(s, seed);
}

console.log(x64hash128('123', 31));