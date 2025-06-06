// Set Spotify authentication cookies
const cookies = [
  {
    name: 'sp_dc',
    value: 'AQBDTUg0PkTORoQui8pDynba2MtByEhH3Zc-jWjJRiWSMNJUY7QNHrTfWRv-S307hkZQOwjQVRYc_oWRwMU1jUa0ePE2yydzQXtECQh2YDR3DFmxpt6FCNT6w7RGai7o85bCSl86vuxt0kUKWYFsBDPRMueV5sDppkESI2lGVJDQWytwa2TqWbDZxmFUuuvgy0K3AfKMu3fVWV1aIQ',
    domain: '.spotify.com',
    path: '/',
    httpOnly: true,
    secure: true
  },
  {
    name: 'sp_key',
    value: 'b994c6cf-b05e-4a7b-85ed-51f032bc4800',
    domain: '.spotify.com',
    path: '/',
    httpOnly: false,
    secure: true
  },
  {
    name: 'sp_t',
    value: '03a630081d956ead15131f1270f8577f',
    domain: '.spotify.com',
    path: '/',
    httpOnly: false,
    secure: true
  }
];

for (const cookie of cookies) {
  await page.context().addCookies([cookie]);
}
EOF < /dev/null