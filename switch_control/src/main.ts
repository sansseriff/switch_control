import './app.css'
import App from './App.svelte'
import { mount } from 'svelte';

// const app = new App({
//   target: document.getElementById('app'),
// })


const app = mount(App, { target: document.getElementById("app") });

export default app

// polyfills
// if (!Array.prototype.findLast) {
//     Object.defineProperty(Array.prototype, 'findLast', {
//       value: function (predicate, thisArg) {
//         if (this == null) {
//           throw new TypeError('"this" is null or not defined');
//         }
//         if (typeof predicate !== 'function') {
//           throw new TypeError('predicate must be a function');
//         }
//         const list = Object(this);
//         const length = list.length >>> 0;
//         for (let i = length - 1; i >= 0; i--) {
//           const value = list[i];
//           if (predicate.call(thisArg, value, i, list)) {
//             return value;
//           }
//         }
//         return undefined;
//       },
//       writable: true,
//       configurable: true
//     });
//   }



//   if (!Array.prototype.at) {
//     Array.prototype.at = function(n) {
//       n = Math.trunc(n) || 0;
//       if (n < 0) n += this.length;
//       if (n < 0 || n >= this.length) return undefined;
//       return this[n];
//     };
//   }
  
//   if (!String.prototype.at) {
//     String.prototype.at = function(n) {
//       n = Math.trunc(n) || 0;
//       if (n < 0) n += this.length;
//       if (n < 0 || n >= this.length) return '';
//       return this.charAt(n);
//     };
//   }